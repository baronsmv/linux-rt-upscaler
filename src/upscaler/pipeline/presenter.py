from __future__ import annotations

import logging
from typing import List, Optional, TYPE_CHECKING

from ..shaders import (
    Bloom,
    CAS,
    Clear,
    CopyScaler,
    Deband,
    Delinearize,
    FilmGrain,
    FSRScaler,
    LanczosScaler,
    Linearize,
    LUT,
    NISScaler,
    Vignette,
)
from ..utils import calculate_scaling_rect
from ..vulkan import Texture2D

if TYPE_CHECKING:
    from .osd import OSDManager
    from .swapchain import SwapchainManager
    from ..config import Config
    from ..shaders import Scaler

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
        osd_manager: OSDManager,
        swapchain_manager: SwapchainManager,
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
        self._active_source_texture: Optional[Texture2D] = None

        # --- Helpers ------------------------------------------------------------
        # Linear/Delinear passes
        self._needs_delinearize: bool = True

        self.linearize_pass = Linearize()
        self._linear_tex = None

        self.delinearize_pass = Delinearize()
        self.delinearize_pass.set_target_texture(self.screen_tex)

        # Clear pass
        self.clear_pass = Clear()
        self.clear_pass.set_target_texture(self.screen_tex)

        # --- Scalers ------------------------------------------------------------
        # Copy
        self._copy = CopyScaler()
        self._copy.set_target_texture(self.screen_tex)

        # Lanczos
        self._lanczos = LanczosScaler()
        self._lanczos.set_target_texture(self.screen_tex)
        self._lanczos.configure(
            blur=self.config.lanczos_blur,
            antiring_strength=self.config.lanczos_antiring_strength,
            tight_antiring=self.config.lanczos_tight_antiring,
        )

        # FSR
        self._fsr = FSRScaler()
        self._fsr.set_target_texture(self.screen_tex)

        # NIS
        self._nis = NISScaler()
        self._nis.set_target_texture(self.screen_tex)

        # --- Post-processing passes (only created if config enables them) ------
        # Debanding (needs separate textures)
        self._deband: Optional[Deband] = None
        self._deband_tex: Optional[Texture2D] = None  # temp debanded output
        if config.deband_enabled:
            self._deband = Deband()
            logger.debug("Deband pass created")

        # CAS (in-place)
        self._cas: Optional[CAS] = None
        if config.cas_enabled:
            self._cas = CAS()
            self._cas.set_target_texture(self.screen_tex)
            logger.debug("CAS pass created")

        # Bloom (in-place)
        self._bloom: Optional[Bloom] = None
        if config.bloom_enabled:
            self._bloom = Bloom()
            self._bloom.set_target_texture(self.screen_tex)
            logger.debug("Bloom pass created")

        # Vignette (in-place)
        self._vignette: Optional[Vignette] = None
        if config.vignette_enabled:
            self._vignette = Vignette()
            self._vignette.set_target_texture(self.screen_tex)
            logger.debug("Vignette pass created")

        # LUT (in-place)
        self._lut: Optional[LUT] = None
        if config.lut_enabled:
            self._lut = LUT(preset=config.lut_preset)
            self._lut.set_target_texture(self.screen_tex)
            logger.debug("LUT pass created")

        # Film grain (in-place)
        self._grain: Optional[FilmGrain] = None
        if config.grain_enabled:
            self._grain = FilmGrain()
            self._grain.set_target_texture(self.screen_tex)
            logger.debug("Film grain pass created")

        # Frame counter - incremented each frame for temporal effects
        self._frame_counter: int = 0

    # ------------------------------------------------------------------
    #  Public API
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
            logger.warning("No source texture set, skipping present")
            return

        # ---- Debanding ------------------------------------------------------
        src = self._apply_deband_if_enabled(src)
        self._active_source_texture = src

        # ---- Linearize and scale --------------------------------------------
        r_x, r_y, r_w, r_h, dst_x, dst_y = self._compute_scaling_params(
            src.width, src.height
        )
        data = src, src.width, src.height, dst_x, dst_y, r_w, r_h
        if r_w == src.width and r_h == src.height:
            self._scale(self._copy, *data)
        elif r_w >= src.width or r_h >= src.height:
            self._scale(self._fsr, *data)
        else:
            self._scale(self._lanczos, *data)

        # ---- CAS ------------------------------------------------------------
        self._apply_cas_if_enabled()

        # ---- Bloom ----------------------------------------------------------
        self._apply_bloom_if_enabled()

        # ---- Vignette -------------------------------------------------------
        self._apply_vignette_if_enabled()

        # ---- Delinearize ----------------------------------------------------
        if self._needs_delinearize:
            self.delinearize_pass.set_source_texture(self.screen_tex)
            self.delinearize_pass.dispatch_auto()

        # ---- LUT ------------------------------------------------------------
        self._apply_lut_if_enabled()

        # ---- Film grain -----------------------------------------------------
        self._apply_grain_if_enabled()

        # ---- OSD blend ------------------------------------------------------
        self.osd.blend_active(self.screen_tex)

        # ---- Swapchain present ----------------------------------------------
        self.swapchain.present(self.screen_tex, wait_for_fence=wait_for_fence)

        # ---- Advance frame counter ------------------------------------------
        self._frame_counter += 1

    def present_unchanged(self):
        """Re-present the current screen texture without any processing."""
        self.swapchain.present(self.screen_tex, wait_for_fence=False)

    def reconfigure_effects(self, config: Config) -> None:
        """Update post-processing passes to match a new configuration."""
        self.config = config

        # ---- Lanczos ----
        self._lanczos.configure(
            blur=self.config.lanczos_blur,
            antiring_strength=self.config.lanczos_antiring_strength,
            tight_antiring=self.config.lanczos_tight_antiring,
        )

        # ---- Debanding ----
        if config.deband_enabled:
            if self._deband is None:
                self._deband = Deband()
        else:
            if self._deband is not None:
                self._deband = None
                self._deband_tex = None

        # ---- CAS ----
        if config.cas_enabled:
            if self._cas is None:
                self._cas = CAS()
                self._cas.set_target_texture(self.screen_tex)
        else:
            if self._cas is not None:
                self._cas = None

        # ---- Bloom ----
        if config.bloom_enabled:
            if self._bloom is None:
                self._bloom = Bloom()
                self._bloom.set_target_texture(self.screen_tex)
        else:
            if self._bloom is not None:
                self._bloom = None

        # ---- Vignette ----
        if config.vignette_enabled:
            if self._vignette is None:
                self._vignette = Vignette()
                self._vignette.set_target_texture(self.screen_tex)
        else:
            if self._vignette is not None:
                self._vignette = None

        # ---- LUT ----
        if config.lut_enabled:
            self._lut = LUT(preset=config.lut_preset)
            self._lut.set_target_texture(self.screen_tex)
        else:
            self._lut = None

        # ---- Film Grain ----
        if config.grain_enabled:
            if self._grain is None:
                self._grain = FilmGrain()
                self._grain.set_target_texture(self.screen_tex)
        else:
            if self._grain is not None:
                self._grain = None

        # Reset cached compute pipelines that reference the old screen texture
        self.osd.clear_compute_cache()

    def get_scaling_rect(self, scale_factor: Optional[float]) -> List[float]:
        """
        Return the rectangle (in overlay widget coordinates) where content is
        drawn. Used by the overlay window for mouse-event mapping.
        """
        src_tex = self._active_source_texture
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
        self._lanczos.set_target_texture(self.screen_tex)
        self._copy.set_target_texture(self.screen_tex)
        for pass_ in (self._cas, self._bloom, self._vignette, self._lut, self._grain):
            if pass_ is not None:
                pass_.set_target_texture(self.screen_tex)

        self.osd.clear_compute_cache()

    def close(self) -> None:
        """Release all GPU resources while the Vulkan device is still alive."""
        self._nis = None
        self._fsr = None
        self._lanczos = None
        self._copy = None

        self.linearize_pass = None
        self.delinearize_pass = None
        self.clear_pass = None

        self._deband = None
        self._deband_tex = None
        self._cas = None
        self._bloom = None
        self._vignette = None
        self._lut = None
        self._grain = None

        self._linear_tex = None
        self.screen_tex = None

    # ------------------------------------------------------------------
    #  Internal helpers
    # ------------------------------------------------------------------

    def _scale(
        self,
        scaler: Scaler,
        src: Texture2D,
        src_width: int,
        src_height: int,
        dst_x: int,
        dst_y: int,
        r_w: int,
        r_h: int,
    ) -> None:
        # Remember whether the output is linear
        self._needs_delinearize = scaler.linear_output

        if not scaler.requires_linear_input:
            # Clear the whole screen with the background color
            self.clear_pass.update_constants(self.background_color)
            self.clear_pass.dispatch_auto()

            # Only scaler pass, no linearize and no background color
            scaler.set_source_texture(src)
            scaler.update_constants(
                src_width=src_width,
                src_height=src_height,
                dst_width=self.screen_width,
                dst_height=self.screen_height,
                dst_x=dst_x,
                dst_y=dst_y,
                dst_w=r_w,
                dst_h=r_h,
            )
            scaler.dispatch_auto()
            return

        # Ensure the intermediate linear texture exists
        if (
            self._linear_tex is None
            or self._linear_tex.width != src_width
            or self._linear_tex.height != src_height
        ):
            self._linear_tex = Texture2D(src_width, src_height)

        # Linearization pass
        self.linearize_pass.set_source_texture(src)
        self.linearize_pass.set_target_texture(self._linear_tex)

        # Scaler pass
        scaler.set_source_texture(self._linear_tex)
        scaler.update_constants(
            background_color=self.background_color,
            src_width=src_width,
            src_height=src_height,
            dst_width=self.screen_width,
            dst_height=self.screen_height,
            dst_x=dst_x,
            dst_y=dst_y,
            dst_w=r_w,
            dst_h=r_h,
        )

        # Combined dispatch
        sequence = [
            (
                self.linearize_pass.compute,
                (src_width + 15) // 16,
                (src_height + 15) // 16,
                1,
                b"",
            ),
            (
                scaler.compute,
                (self.screen_width + 15) // 16,
                (self.screen_height + 15) // 16,
                1,
                b"",
            ),
        ]
        self.linearize_pass.compute.dispatch_sequence(sequence)

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

    def _compute_scaling_params(self, src_width: int, src_height: int):
        """
        Compute the destination rectangle and screen position.
        Returns (r_x, r_y, r_w, r_h, dst_x, dst_y).
        """
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
        return r_x, r_y, r_w, r_h, dst_x, dst_y
