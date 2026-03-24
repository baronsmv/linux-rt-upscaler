from typing import Tuple


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
