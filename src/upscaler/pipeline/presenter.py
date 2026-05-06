import logging
import math
from typing import List, Optional, TYPE_CHECKING

from ..config import Config
from ..shaders import (
    LanczosScaler,
    CASPass,
    BloomPass,
    VignettePass,
    FilmGrainPass,
    LUTPass,
    DebandPass,
)
from ..utils import calculate_scaling_rect
from ..vulkan import Texture2D

if TYPE_CHECKING:
    from .osd import OSDManager

logger = logging.getLogger(__name__)


class Presenter:
    """
    Manages the screen texture and all post-processing passes.

    The processing chain (executed in :meth:`present`):
        1. Optional debanding (uses a temporary texture).
        2. Lanczos scaling.
        3. Optional contrast adaptive sharpening (CAS).
        4. Optional bloom.
        5. Optional vignette.
        6. Optional color grading (3D LUT).
        7. Optional film grain.
        8. OSD blending.
        9. Swapchain presentation.

    All passes that operate on the final screen image (CAS through grain) work
    in-place on `self.screen_tex`. Debanding uses a dedicated intermediate
    texture because read-after-write would be unsafe.

    Effect parameters are taken directly from the :class:`Config` instance.
    """

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        content_width: int,
        content_height: int,
        scale_mode: str,
        config: Config,
        osd_manager: "OSDManager",
        swapchain_manager,
    ) -> None:
        # --- dimensions & layout ------------------------------------------------
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.content_width = content_width
        self.content_height = content_height
        self.scale_mode = scale_mode
        self.background_color = config.background_color
        self.offset_x = config.offset_x
        self.offset_y = config.offset_y

        # --- Saved objects ----------------------------------------------------
        self.config = config
        self.osd = osd_manager
        self.swapchain = swapchain_manager

        # --- Screen texture (rendered by Lanczos and all post-FX) ---------------
        self.screen_tex = Texture2D(screen_width, screen_height)

        # --- Lanczos scaler -----------------------------------------------------
        self.lanczos = LanczosScaler()
        self.lanczos.set_target_texture(self.screen_tex)

        # --- Post-processing passes (only created if config enables them) ------
        # Debanding (needs separate textures)
        self._deband: Optional[DebandPass] = None
        self._deband_tex: Optional[Texture2D] = None  # temp debanded output
        if config.deband_enabled:
            self._deband = DebandPass()
            logger.debug("Deband pass created")

        # CAS (in-place)
        self._cas: Optional[CASPass] = None
        if config.cas_enabled:
            self._cas = CASPass()
            self._cas.set_target_texture(self.screen_tex)
            logger.debug("CAS pass created")

        # Bloom (in-place)
        self._bloom: Optional[BloomPass] = None
        if config.bloom_enabled:
            self._bloom = BloomPass()
            self._bloom.set_target_texture(self.screen_tex)
            logger.debug("Bloom pass created")

        # Vignette (in-place)
        self._vignette: Optional[VignettePass] = None
        if config.vignette_enabled:
            self._vignette = VignettePass()
            self._vignette.set_target_texture(self.screen_tex)
            logger.debug("Vignette pass created")

        # LUT (in-place)
        self._lut: Optional[LUTPass] = None
        if config.lut_enabled:
            self._lut = LUTPass(preset=config.lut_preset)
            self._lut.set_target_texture(self.screen_tex)
            logger.debug("LUT pass created")

        # Film grain (in-place)
        self._grain: Optional[FilmGrainPass] = None
        if config.grain_enabled:
            self._grain = FilmGrainPass()
            self._grain.set_target_texture(self.screen_tex)
            logger.debug("Film grain pass created")

        # Frame counter - incremented each frame for temporal effects
        self._frame_counter: int = 0

    # ------------------------------------------------------------------
    #  Public API - called from Pipeline
    # ------------------------------------------------------------------

    def set_upscaled_source(self, texture: Texture2D) -> None:
        """
        Store the raw upscaled texture (before any post-processing).

        This texture will be used as the starting point in the next
        :meth:`present` call; it may be optionally debanded before
        scaling.
        """
        self._raw_upscaled_tex = texture

    def present(self, wait_for_fence: bool = False) -> None:
        """
        Run the entire post-processing chain and present to the swapchain.

        Steps:
          1. Deband (if enabled) -> writes to `_deband_tex`.
          2. Lanczos scaling.
          3. CAS -> bloom -> vignette -> LUT -> grain (each only if enabled).
          4. OSD overlay blend.
          5. Swapchain present.
          6. Increment frame counter.
        """
        src = self._raw_upscaled_tex
        if src is None:
            logger.warning("No source texture set - skipping present.")
            return

        # ---- 1. Debanding (optional) -----------------------------------------
        src = self._apply_deband_if_enabled(src)

        # ---- 2. Lanczos scaling ---------------------------------------------
        self.lanczos.set_source_texture(src)
        self._update_lanczos_constants(src.width, src.height)
        self.lanczos.dispatch_auto()

        # ---- 3. CAS ----------------------------------------------------------
        self._apply_cas_if_enabled()

        # ---- 4. Bloom --------------------------------------------------------
        self._apply_bloom_if_enabled()

        # ---- 5. Vignette -----------------------------------------------------
        self._apply_vignette_if_enabled()

        # ---- 6. LUT ----------------------------------------------------------
        self._apply_lut_if_enabled()

        # ---- 7. Film grain ---------------------------------------------------
        self._apply_grain_if_enabled()

        # ---- 8. OSD blend (always) -------------------------------------------
        self.osd.blend_active(self.screen_tex)

        # ---- 9. Swapchain present --------------------------------------------
        self.swapchain.present(self.screen_tex, wait_for_fence=wait_for_fence)

        # ---- 10. Advance frame counter ---------------------------------------
        self._frame_counter += 1

    def present_unchanged(self):
        """Re-present the current screen texture without any processing."""
        self.swapchain.present(self.screen_tex)

    def get_scaling_rect(self, scale_factor: float) -> List[float]:
        """
        Return the rectangle (in overlay widget coordinates) where content is
        drawn. Used by the overlay window for mouse-event mapping.
        """
        src_tex = self.lanczos.source_texture
        if src_tex is None:
            return [0, 0, 0, 0]

        r_x, r_y, r_w, r_h = calculate_scaling_rect(
            src_tex.width,
            src_tex.height,
            self.content_width,
            self.content_height,
            self.scale_mode,
        )

        canvas_x = (self.screen_width - self.content_width) // 2
        canvas_y = (self.screen_height - self.content_height) // 2
        dst_x = canvas_x + r_x + self.offset_x
        dst_y = canvas_y + r_y + self.offset_y

        return [
            dst_x / scale_factor,
            dst_y / scale_factor,
            r_w / scale_factor,
            r_h / scale_factor,
        ]

    def resize(self, new_width: int, new_height: int) -> None:
        """
        Handle overlay window resize.
        Re-creates the screen texture and rebinds it to every in-place pass.
        """
        self.screen_width = new_width
        self.screen_height = new_height
        self.screen_tex = Texture2D(new_width, new_height)

        # Rebind screen texture to all passes
        self.lanczos.set_target_texture(self.screen_tex)
        for pass_ in (self._cas, self._bloom, self._vignette, self._lut, self._grain):
            if pass_ is not None:
                pass_.set_target_texture(self.screen_tex)

        self.osd.clear_compute_cache()

    # ------------------------------------------------------------------
    #  Internal helpers - one per effect, to keep `present()` clean
    # ------------------------------------------------------------------

    def _apply_deband_if_enabled(self, src: Texture2D) -> Texture2D:
        """Run the debanding pass if enabled; return the (possibly debanded) texture."""
        if self._deband is None or not self.config.deband_enabled:
            return src

        # Ensure we have a compatible target texture
        if (
            self._deband_tex is None
            or self._deband_tex.width != src.width
            or self._deband_tex.height != src.height
        ):
            self._deband_tex = Texture2D(src.width, src.height)

        # Set source first, then target (order doesn't matter with the guard)
        self._deband.set_source_texture(src)
        self._deband.set_target_texture(self._deband_tex)

        self._deband.update_constants(
            strength=self.config.deband_strength,
            frame_index=self._frame_counter,  # temporal dither
        )
        self._deband.dispatch_auto()
        return self._deband_tex

    def _apply_cas_if_enabled(self) -> None:
        if self._cas is not None and self.config.cas_enabled:
            self._cas.update_constants(strength=self.config.cas_strength)
            self._cas.dispatch_auto()

    def _apply_bloom_if_enabled(self) -> None:
        if self._bloom is not None and self.config.bloom_enabled:
            self._bloom.update_constants(
                strength=self.config.bloom_strength,
                threshold=self.config.bloom_threshold,
                radius=self.config.bloom_radius,
            )
            self._bloom.dispatch_auto()

    def _apply_vignette_if_enabled(self) -> None:
        if self._vignette is not None and self.config.vignette_enabled:
            self._vignette.update_constants(
                strength=self.config.vignette_strength,
                radius=self.config.vignette_radius,
                falloff=self.config.vignette_falloff,
            )
            self._vignette.dispatch_auto()

    def _apply_lut_if_enabled(self) -> None:
        if self._lut is not None and self.config.lut_enabled:
            self._lut.update_constants(intensity=self.config.lut_intensity)
            self._lut.dispatch_auto()

    def _apply_grain_if_enabled(self) -> None:
        if self._grain is not None and self.config.grain_enabled:
            self._grain.update_constants(
                strength=self.config.grain_strength,
                grain_size=self.config.grain_size,
                frame_index=self._frame_counter,
            )
            self._grain.dispatch_auto()

    def _update_lanczos_constants(self, src_width: int, src_height: int) -> None:
        """Compute destination rectangle and upload Lanczos constants."""
        r_x, r_y, r_w, r_h = calculate_scaling_rect(
            src_width,
            src_height,
            self.content_width,
            self.content_height,
            self.scale_mode,
        )
        canvas_x = (self.screen_width - self.content_width) // 2
        canvas_y = (self.screen_height - self.content_height) // 2
        dst_x = canvas_x + r_x + self.offset_x
        dst_y = canvas_y + r_y + self.offset_y
        scale_x = r_w / src_width
        scale_y = r_h / src_height
        radius_x = 2 if scale_x >= 1.0 else math.ceil(2.0 / scale_x)
        radius_y = 2 if scale_y >= 1.0 else math.ceil(2.0 / scale_y)

        if r_w <= 0 or r_h <= 0:
            logger.warning(f"Invalid Lanczos rect: {r_w}x{r_h}, skipping update")
            return

        self.lanczos.update_constants(
            self.background_color,
            src_width,
            src_height,
            self.screen_width,
            self.screen_height,
            dst_x,
            dst_y,
            r_w,
            r_h,
            radius_x=radius_x,
            radius_y=radius_y,
            blur=self.config.lanczos_blur,
            antiring_strength=self.config.lanczos_antiring_strength,
            linear_light=self.config.lanczos_linear_light,
            tight_antiring=self.config.lanczos_tight_antiring,
        )
