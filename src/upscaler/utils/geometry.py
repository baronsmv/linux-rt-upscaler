from typing import Tuple


def parse_output_geometry(
    geometry: str, src_w: int, src_h: int, base_w: int, base_h: int
) -> Tuple[int, int, int, int, str]:
    """
    Returns (overlay_w, overlay_h, content_w, content_h, mode)

    Recognised formats:
      - "stretch", "fit", "cover"          (use full monitor, mode = name)
      - "50%"                               (50% of monitor, fit content)
      - "50%!"                              (50% of monitor, stretch content)
      - "1920x"                              (width fixed, height proportional, fit)
      - "1920x!"                             (width fixed, height proportional, stretch)
      - "x1080"                              (height fixed, width proportional, fit)
      - "x1080!"                             (height fixed, width proportional, stretch)
      - "1920x1080"                          (exact size, fit content)
      - "1920x1080!"                         (exact size, stretch)
      - "1920x1080^"                         (exact size, cover)
    """
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
    if geometry.endswith("%") or geometry.endswith("%!"):
        stretch = geometry.endswith("!")
        if stretch:
            geom = geometry[:-2]  # remove "%!"
        else:
            geom = geometry[:-1]  # remove "%"
        percent = float(geom) / 100.0
        ow = int(base_w * percent)
        oh = int(base_h * percent)
        mode = "stretch" if stretch else "fit"
        if mode == "stretch":
            cw, ch = ow, oh
        else:
            scale = min(ow / src_w, oh / src_h)
            cw, ch = int(src_w * scale), int(src_h * scale)
        return ow, oh, cw, ch, mode

    # Wx   (width fixed, height proportional)
    if (geometry.endswith("x") or geometry.endswith("x!")) and len(geometry) > 1:
        stretch = geometry.endswith("!")
        if stretch:
            geom = geometry[:-2]  # remove "x!"
        else:
            geom = geometry[:-1]  # remove "x"
        ow = int(geom)
        scale = ow / src_w
        oh = int(src_h * scale)
        mode = "stretch" if stretch else "fit"
        if mode == "stretch":
            cw, ch = ow, oh
        else:
            cw, ch = int(src_w * scale), int(src_h * scale)
        return ow, oh, cw, ch, mode

    # xH   (height fixed, width proportional)
    if (geometry.startswith("x") or geometry.startswith("x!")) and len(geometry) > 1:
        stretch = geometry.endswith("!")
        if stretch:
            geom = geometry[1:-1]  # remove leading "x" and trailing "!"
        else:
            geom = geometry[1:]  # remove leading "x"
        oh = int(geom)
        scale = oh / src_h
        ow = int(src_w * scale)
        mode = "stretch" if stretch else "fit"
        if mode == "stretch":
            cw, ch = ow, oh
        else:
            cw, ch = int(src_w * scale), int(src_h * scale)
        return ow, oh, cw, ch, mode

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

    # Fallback: treat as exact WxH (stretch)
    if "x" in geometry:
        parts = geometry.split("x")
        if len(parts) == 2:
            ow, oh = int(parts[0]), int(parts[1])
            return ow, oh, ow, oh, "stretch"

    raise ValueError(f"Invalid geometry: {geometry}")


def calculate_scaling_rect(
    src_w: int, src_h: int, dst_w: int, dst_h: int, mode: str
) -> Tuple[int, int, int, int]:
    """
    Returns (x, y, w, h) where (x, y) is the top‑left corner of the
    destination rectangle within the output texture of size dst_w x dst_h.
    """
    if mode == "stretch":
        return 0, 0, dst_w, dst_h

    if mode == "cover":
        scale = max(dst_w / src_w, dst_h / src_h)
    else:  # "fit" or any unknown mode (fallback to fit)
        scale = min(dst_w / src_w, dst_h / src_h)

    out_w = int(src_w * scale)
    out_h = int(src_h * scale)
    out_x = (dst_w - out_w) // 2
    out_y = (dst_h - out_h) // 2
    return out_x, out_y, out_w, out_h
