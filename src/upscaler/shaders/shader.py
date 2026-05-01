import logging
from abc import ABC, abstractmethod
from typing import Optional

from ..vulkan import Buffer, Compute, Sampler, Texture2D

logger = logging.getLogger(__name__)


class ShaderPass(ABC):
    """
    Abstract base class for a single-dispatch compute shader pass.

    Responsibilities:
        * Load SPIR-V shader from disk.
        * Maintain a constant buffer (subclasses define its layout).
        * (Re)create the Vulkan compute pipeline when textures change.
        * Provide a safe `dispatch_auto()` that covers the target texture
          with 16x16 workgroups.

    Subclasses must implement
        :meth:`_get_bindings`
        :meth:`update_constants`
        :meth:`_cb_size`

    and can optionally override
        :meth:`_create_persistent_resources`   (to create samplers etc.)

    Attributes:
        shader_path (str): Path to the compiled SPIR-V file.
        target_texture (Texture2D | None): The output texture (UAV).
        _shader (bytes | None): Shader bytecode, cached after loading.
        _cb (Buffer | None): Constant buffer.
        _sampler (Sampler | None): Optional sampler for the pass.
        _compute (Compute | None): The compute pipeline object.
    """

    # ------------------------------------------------------------------
    #  Subclass interface (must be implemented)
    # ------------------------------------------------------------------

    @abstractmethod
    def _get_bindings(self):
        """
        Return the Vulkan resource lists for pipeline creation.

        Returns:
            tuple: (list_of_srv, list_of_uav, list_of_samplers)
                The SRV list typically contains the source texture
                (if any) and the UAV list contains the target texture.
                Samplers can be empty if not needed.
        """

    @abstractmethod
    def update_constants(self, **kwargs) -> None:
        """
        Pack pass-specific parameters into the constant buffer and upload.

        Implementations must call `self._cb.upload(data)` with the packed
        bytes.  The method signature is free-form; subclasses should
        document each keyword argument.

        Raises:
            RuntimeError: if the constant buffer has not been created yet
                (target texture not set).
        """

    @staticmethod
    @abstractmethod
    def _cb_size() -> int:
        """
        Return the constant buffer size in bytes for this pass.

        Must match the HLSL `cbuffer` layout (with proper padding).
        """

    # ------------------------------------------------------------------
    #  Optional overrides
    # ------------------------------------------------------------------

    def _create_persistent_resources(self) -> None:
        """
        Create Vulkan resources that survive texture changes.

        The default implementation creates a constant buffer of the
        size returned by :meth:`_cb_size`.  Subclasses that need a
        sampler should call `super()._create_persistent_resources()`
        and then create their sampler(s).
        """
        self._cb = Buffer(self._cb_size())

    def set_source_texture(self, tex: Texture2D) -> None:
        """
        Set a separate **source** texture (SRV).  Not all passes
        need a distinct source; those that do should override this
        method to store the texture and rebuild the pipeline.

        The default implementation raises `NotImplementedError`.
        """
        raise NotImplementedError(
            f"{type(self).__name__} does not support a separate source texture"
        )

    # ------------------------------------------------------------------
    #  Initialisation (customisation point)
    # ------------------------------------------------------------------

    def __init__(self, shader_path: str) -> None:
        """
        Load the shader and create persistent Vulkan resources.

        Args:
            shader_path: Absolute or relative path to the SPIR-V file.
        """
        self._shader_path = shader_path
        self._shader: Optional[bytes] = None
        self._sampler: Optional[Sampler] = None
        self._cb: Optional[Buffer] = None
        self._compute: Optional[Compute] = None
        self.target_texture: Optional[Texture2D] = None

        self._load_shader()
        self._create_persistent_resources()

    # ------------------------------------------------------------------
    #  Shared functionality (normally not overridden)
    # ------------------------------------------------------------------

    def _load_shader(self) -> None:
        """Read the SPIR-V binary into memory."""
        try:
            with open(self._shader_path, "rb") as f:
                self._shader = f.read()
            logger.debug(
                "%s shader loaded from %s", type(self).__name__, self._shader_path
            )
        except OSError as e:
            raise RuntimeError(
                f"Failed to load {type(self).__name__} shader at {self._shader_path}: {e}"
            ) from e

    def set_target_texture(self, tex: Texture2D) -> None:
        """
        Bind the output texture (UAV).  Rebuilds the compute pipeline
        if the texture object changes.

        Args:
            tex: The RGBA8 texture to write results into.
        """
        if tex is self.target_texture:
            return
        self.target_texture = tex
        self._rebuild_compute()

    def _rebuild_compute(self) -> None:
        """Create a fresh compute pipeline from the current bindings."""
        if self.target_texture is None:
            return

        srvs, uavs, samplers = self._get_bindings()

        self._compute = Compute(
            self._shader,
            srv=srvs if srvs else None,
            uav=uavs if uavs else None,
            cbv=[self._cb],
            samplers=samplers if samplers else None,
            push_size=0,
        )
        logger.debug("%s compute pipeline rebuilt", type(self).__name__)

    def _check_ready(self) -> None:
        """Raise if the pipeline is not yet ready."""
        if self._compute is None:
            raise RuntimeError(
                f"{type(self).__name__} pipeline is not ready - "
                "call set_target_texture() (and set_source_texture() if needed) first."
            )

    # ------------------------------------------------------------------
    #  Dispatch
    # ------------------------------------------------------------------

    def dispatch_auto(self) -> None:
        """
        Dispatch with workgroup counts that cover the entire target texture.

        Uses 16x16 thread groups.
        """
        self._check_ready()
        w, h = self.target_texture.width, self.target_texture.height
        self.dispatch((w + 15) // 16, (h + 15) // 16)

    def dispatch(self, groups_x: int, groups_y: int, groups_z: int = 1) -> None:
        """
        Execute the compute shader.

        Args:
            groups_x: Number of workgroups in X.
            groups_y: Number of workgroups in Y.
            groups_z: Number of workgroups in Z (always 1).
        """
        self._check_ready()
        self._compute.dispatch(groups_x, groups_y, groups_z)
