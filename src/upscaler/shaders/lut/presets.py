import struct
from typing import Callable, Dict

LUT_SIZE = 32  # 32-x32-x32 - good balance of quality and memory
NUM_PIXELS = LUT_SIZE**3
SLICE_BYTES = LUT_SIZE * LUT_SIZE * 4


# ---------------------------------------------------------------------------
#  Preset builder - define a preset with three channel curves
# ---------------------------------------------------------------------------
def build_lut(
    func_r: Callable[[float, float, float], float],
    func_g: Callable[[float, float, float], float],
    func_b: Callable[[float, float, float], float],
) -> bytes:
    """
    Generate a 32³ RGBA8 LUT by evaluating `func_*` at each lattice point.

    The functions receive normalized input (r, g, b) in [0,1] and should
    return a normalized output channel value.
    """
    data = bytearray(NUM_PIXELS * 4)
    off = 0
    for z in range(LUT_SIZE):
        b_in = z / (LUT_SIZE - 1)
        for y in range(LUT_SIZE):
            g_in = y / (LUT_SIZE - 1)
            for x in range(LUT_SIZE):
                r_in = x / (LUT_SIZE - 1)

                r = max(0.0, min(1.0, func_r(r_in, g_in, b_in)))
                g = max(0.0, min(1.0, func_g(r_in, g_in, b_in)))
                b = max(0.0, min(1.0, func_b(r_in, g_in, b_in)))

                data[off : off + 4] = struct.pack(
                    "BBBB",
                    int(r * 255),
                    int(g * 255),
                    int(b * 255),
                    255,
                )
                off += 4
    return bytes(data)


# ---------------------------------------------------------------------------
#  Preset definitions
# ---------------------------------------------------------------------------


def _identity() -> bytes:
    """Identity LUT - pass-through (no color change)."""

    def r(r_in, g_in, b_in):
        return r_in

    def g(r_in, g_in, b_in):
        return g_in

    def b(r_in, g_in, b_in):
        return b_in

    return build_lut(r, g, b)


def _warm_sunset() -> bytes:
    """Golden-hour look: strengthens reds and oranges, cools shadows slightly."""

    def r(r_in, g_in, b_in):
        return r_in * 1.05 + 0.02  # slight red boost

    def g(r_in, g_in, b_in):
        return g_in * 0.98 + 0.01  # keep greens mostly natural

    def b(r_in, g_in, b_in):
        return b_in * 0.92 - 0.01  # blue desaturation

    return build_lut(r, g, b)


def _cool_night() -> bytes:
    """Cool, moonlit tint: lifts blues, slightly mutes warm tones."""

    def r(r_in, g_in, b_in):
        return r_in * 0.95

    def g(r_in, g_in, b_in):
        return g_in * 1.02

    def b(r_in, g_in, b_in):
        return min(1.0, b_in * 1.08 + 0.02)

    return build_lut(r, g, b)


def _film_stock() -> bytes:
    """Subtle S-curve + desaturation: mimics a classic film print."""

    def s_curve(v):
        # Symmetric S-curve that leaves 0 and 1 unchanged
        if v < 0.5:
            return 2.0 * v * v
        else:
            return 1.0 - pow(-2.0 * v + 2.0, 2.0) / 2.0

    def r(r_in, g_in, b_in):
        luma = 0.2126 * r_in + 0.7152 * g_in + 0.0722 * b_in
        return r_in * 0.92 + (s_curve(luma) - luma) * 0.1

    def g(r_in, g_in, b_in):
        luma = 0.2126 * r_in + 0.7152 * g_in + 0.0722 * b_in
        return g_in * 0.92 + (s_curve(luma) - luma) * 0.1

    def b(r_in, g_in, b_in):
        luma = 0.2126 * r_in + 0.7152 * g_in + 0.0722 * b_in
        return b_in * 0.92 + (s_curve(luma) - luma) * 0.1

    return build_lut(r, g, b)


def _vivid() -> bytes:
    """Increased saturation without affecting overall brightness."""

    def r(r_in, g_in, b_in):
        luma = 0.2126 * r_in + 0.7152 * g_in + 0.0722 * b_in
        return luma + (r_in - luma) * 1.2

    def g(r_in, g_in, b_in):
        luma = 0.2126 * r_in + 0.7152 * g_in + 0.0722 * b_in
        return luma + (g_in - luma) * 1.2

    def b(r_in, g_in, b_in):
        luma = 0.2126 * r_in + 0.7152 * g_in + 0.0722 * b_in
        return luma + (b_in - luma) * 1.2

    return build_lut(r, g, b)


def _soft_pastel() -> bytes:
    """Lightens and softly desaturates - dreamy pastel look."""

    def r(r_in, g_in, b_in):
        return min(1.0, r_in * 0.95 + 0.08)

    def g(r_in, g_in, b_in):
        return min(1.0, g_in * 0.95 + 0.08)

    def b(r_in, g_in, b_in):
        return min(1.0, b_in * 0.95 + 0.08)

    return build_lut(r, g, b)


def _noir() -> bytes:
    """High contrast black-and-white film noir look."""

    def gray(r_in, g_in, b_in):
        luma = 0.2126 * r_in + 0.7152 * g_in + 0.0722 * b_in
        # increase contrast
        luma = (luma - 0.5) * 1.2 + 0.5
        return max(0.0, min(1.0, luma))

    return build_lut(gray, gray, gray)


def _sepia() -> bytes:
    """Classic sepia tone - old-photograph warmth, slightly faded."""

    def r(r_in, g_in, b_in):
        luma = 0.2126 * r_in + 0.7152 * g_in + 0.0722 * b_in
        return min(1.0, luma * 1.12 + 0.08)

    def g(r_in, g_in, b_in):
        luma = 0.2126 * r_in + 0.7152 * g_in + 0.0722 * b_in
        return min(1.0, luma * 0.95 + 0.04)

    def b(r_in, g_in, b_in):
        luma = 0.2126 * r_in + 0.7152 * g_in + 0.0722 * b_in
        return min(1.0, luma * 0.78)

    return build_lut(r, g, b)


def _bleach() -> bytes:
    """Bleach-bypass: high contrast, metallic desaturation."""

    def r(r_in, g_in, b_in):
        luma = 0.2126 * r_in + 0.7152 * g_in + 0.0722 * b_in
        luma_contrast = max(0.0, min(1.0, (luma - 0.5) * 1.3 + 0.5))
        return r_in * 0.7 + luma_contrast * 0.3

    def g(r_in, g_in, b_in):
        luma = 0.2126 * r_in + 0.7152 * g_in + 0.0722 * b_in
        luma_contrast = max(0.0, min(1.0, (luma - 0.5) * 1.3 + 0.5))
        return g_in * 0.7 + luma_contrast * 0.3

    def b(r_in, g_in, b_in):
        luma = 0.2126 * r_in + 0.7152 * g_in + 0.0722 * b_in
        luma_contrast = max(0.0, min(1.0, (luma - 0.5) * 1.3 + 0.5))
        return b_in * 0.7 + luma_contrast * 0.3

    return build_lut(r, g, b)


def _split_tone() -> bytes:
    """Split-tone: cyan shadows, orange highlights - cinematic music video look."""

    def r(r_in, g_in, b_in):
        luma = 0.2126 * r_in + 0.7152 * g_in + 0.0722 * b_in
        # orange highlight tint (R=1.0, G=0.7, B=0.3) * luma^2
        highlight = luma * luma
        return r_in * (1.0 - highlight) + highlight * 1.0

    def g(r_in, g_in, b_in):
        luma = 0.2126 * r_in + 0.7152 * g_in + 0.0722 * b_in
        highlight = luma * luma
        # shadow cyan tint (R=0, G=0.3, B=0.5) * (1-luma)
        shadow = (1.0 - luma) * 0.3
        return g_in * (1.0 - highlight - shadow) + highlight * 0.7 + shadow

    def b(r_in, g_in, b_in):
        luma = 0.2126 * r_in + 0.7152 * g_in + 0.0722 * b_in
        highlight = luma * luma
        shadow = (1.0 - luma) * 0.5
        return b_in * (1.0 - highlight - shadow) + highlight * 0.3 + shadow

    return build_lut(r, g, b)


def _cyano() -> bytes:
    """Cyanotype: monochrome blue-cyan tint, like a blueprint."""

    def r(r_in, g_in, b_in):
        luma = 0.2126 * r_in + 0.7152 * g_in + 0.0722 * b_in
        return luma * 0.2

    def g(r_in, g_in, b_in):
        luma = 0.2126 * r_in + 0.7152 * g_in + 0.0722 * b_in
        return luma * 0.7

    def b(r_in, g_in, b_in):
        luma = 0.2126 * r_in + 0.7152 * g_in + 0.0722 * b_in
        return luma * 1.0

    return build_lut(r, g, b)


def _lofi() -> bytes:
    """Vintage Lo-Fi: crushed shadows, faded highlights, muted colors."""

    def r(r_in, g_in, b_in):
        r = r_in * 0.9 + 0.05
        if r > 0.5:
            r = r * 0.8 + 0.2
        return r

    def g(r_in, g_in, b_in):
        g = g_in * 0.9 + 0.05
        if g > 0.5:
            g = g * 0.8 + 0.2
        return g

    def b(r_in, g_in, b_in):
        b = b_in * 0.9 + 0.05
        if b > 0.5:
            b = b * 0.8 + 0.2
        return b

    return build_lut(r, g, b)


# ---------------------------------------------------------------------------
#  Preset registry
# ---------------------------------------------------------------------------
BUILT_IN_PRESETS: Dict[str, Callable[[], bytes]] = {
    "identity": _identity,
    "warm": _warm_sunset,
    "cool": _cool_night,
    "split": _split_tone,
    "vivid": _vivid,
    "pastel": _soft_pastel,
    "lofi": _lofi,
    "bleach": _bleach,
    "film": _film_stock,
    "noir": _noir,
    "sepia": _sepia,
    "cyano": _cyano,
}
