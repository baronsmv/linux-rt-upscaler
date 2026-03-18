from PySide6.QtGui import QColor


def color_string_to_float4(color_str: str) -> tuple[float, float, float, float]:
    """Convert '#RRGGBB' or color name to normalized (r,g,b,a)."""
    qcolor = QColor(color_str)
    if not qcolor.isValid():
        qcolor = QColor("black")  # fallback
    return qcolor.redF(), qcolor.greenF(), qcolor.blueF(), qcolor.alphaF()


def parse_output_geometry(
    geometry: str, src_w: int, src_h: int, base_w: int, base_h: int
):
    """
    Returns (overlay_w, overlay_h, content_w, content_h, mode)
    """
    geometry = geometry.strip()

    # Pure mode names (use base overlay size)
    if geometry in ("stretch", "fit", "cover"):
        mode = geometry
        ow, oh = base_w, base_h
        if mode == "stretch":
            cw, ch = ow, oh
        elif mode == "fit":
            scale = min(ow / src_w, oh / src_h)
            cw, ch = int(src_w * scale), int(src_h * scale)
        else:  # cover
            scale = max(ow / src_w, oh / src_h)
            cw, ch = int(src_w * scale), int(src_h * scale)
        return ow, oh, cw, ch, mode

    # Percentage of base overlay
    if geometry.endswith("%"):
        percent = float(geometry[:-1]) / 100.0
        ow = int(base_w * percent)
        oh = int(base_h * percent)
        return ow, oh, ow, oh, "stretch"

    # WxH!  (exact stretch)
    if geometry.endswith("!"):
        geom = geometry[:-1]
        if "x" in geom:
            parts = geom.split("x")
            if len(parts) == 2:
                ow, oh = int(parts[0]), int(parts[1])
                return ow, oh, ow, oh, "stretch"

    # WxH^  (cover)
    if geometry.endswith("^"):
        geom = geometry[:-1]
        if "x" in geom:
            parts = geom.split("x")
            if len(parts) == 2:
                ow, oh = int(parts[0]), int(parts[1])
                scale = max(ow / src_w, oh / src_h)
                cw, ch = int(src_w * scale), int(src_h * scale)
                return ow, oh, cw, ch, "cover"

    # WxH  (fit, letterbox)
    if "x" in geometry and not geometry.startswith("x"):
        parts = geometry.split("x")
        if len(parts) == 2 and parts[0] and parts[1]:
            ow, oh = int(parts[0]), int(parts[1])
            scale = min(ow / src_w, oh / src_h)
            cw, ch = int(src_w * scale), int(src_h * scale)
            return ow, oh, cw, ch, "fit"

    # Wx   (width fixed, height proportional)
    if geometry.endswith("x") and len(geometry) > 1:
        ow = int(geometry[:-1])
        scale = ow / src_w
        oh = int(src_h * scale)
        return ow, oh, ow, oh, "stretch"

    # xH   (height fixed, width proportional)
    if geometry.startswith("x") and len(geometry) > 1:
        oh = int(geometry[1:])
        scale = oh / src_h
        ow = int(src_w * scale)
        return ow, oh, ow, oh, "stretch"

    # Fallback: treat as exact WxH (stretch)
    if "x" in geometry:
        parts = geometry.split("x")
        if len(parts) == 2:
            ow, oh = int(parts[0]), int(parts[1])
            return ow, oh, ow, oh, "stretch"

    raise ValueError(f"Invalid geometry: {geometry}")
