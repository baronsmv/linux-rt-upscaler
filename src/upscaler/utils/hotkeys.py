import logging
from typing import Dict, Iterable, Optional, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
#  Default bindings
# ---------------------------------------------------------------------------
DEFAULT_HOTKEYS: Dict[str, str] = {
    "toggle_scaling": "Alt+Shift+S",
    "exit_app": "Alt+Shift+Escape",
    "screenshot": "Alt+Shift+P",
    "cycle_model": "Alt+Shift+M",
    "cycle_geometry": "Alt+Shift+G",
    "restore_view": "Alt+Shift+R",
    "zoom_in": "Alt+Shift+Plus",
    "zoom_out": "Alt+Shift+Minus",
    "offset_up": "Alt+Shift+Up",
    "offset_down": "Alt+Shift+Down",
    "offset_left": "Alt+Shift+Left",
    "offset_right": "Alt+Shift+Right",
}

HOTKEY_GROUPS: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    ("session", ("toggle_scaling", "exit_app", "screenshot")),
    ("view", ("cycle_model", "cycle_geometry", "restore_view")),
    ("zooming", ("zoom_in", "zoom_out")),
    ("panning", ("offset_left", "offset_right", "offset_up", "offset_down")),
)

# ---------------------------------------------------------------------------
#  Modifier bits
# ---------------------------------------------------------------------------
_MOD_SHIFT = 0x0001
_MOD_CONTROL = 0x0004
_MOD_ALT = 0x0008
_MOD_SUPER = 0x0040

MODIFIER_MAP: Dict[str, int] = {
    "Ctrl": _MOD_CONTROL,
    "Control": _MOD_CONTROL,
    "Alt": _MOD_ALT,
    "Shift": _MOD_SHIFT,
    "Super": _MOD_SUPER,
    "Win": _MOD_SUPER,
}

MODIFIER_ORDER: Tuple[str, ...] = ("Ctrl", "Alt", "Shift", "Super")

# ---------------------------------------------------------------------------
#  Keysyms
# ---------------------------------------------------------------------------
KEYSYM_MAP: Dict[str, int] = {
    **{c: 0x61 + i for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ")},
    **{c: 0x30 + i for i, c in enumerate("0123456789")},
    **{f"F{i}": 0xFFBE + (i - 1) for i in range(1, 13)},
    # Arrows
    "Left": 0xFF51,
    "Up": 0xFF52,
    "Right": 0xFF53,
    "Down": 0xFF54,
    "Insert": 0xFF63,
    "Delete": 0xFFFF,
    "Home": 0xFF50,
    "End": 0xFF57,
    "PageUp": 0xFF55,
    "PageDown": 0xFF56,
    "Print": 0xFF61,
    "Pause": 0xFF13,
    "ScrollLock": 0xFF14,
    "LeftBracket": 0x5B,
    "RightBracket": 0x5D,
    "Backslash": 0x5C,
    "Semicolon": 0x3B,
    "Apostrophe": 0x27,
    "Comma": 0x2C,
    "Period": 0x2E,
    "Slash": 0x2F,
    "Plus": 0x2B,
    "Minus": 0x2D,
    "Equal": 0x3D,
    "Grave": 0x60,
    "Space": 0x20,
    "Return": 0xFF0D,
    "Backspace": 0xFF08,
    "Tab": 0xFF09,
    "Escape": 0xFF1B,
}


# ---------------------------------------------------------------------------
#  Parsing / formatting
# ---------------------------------------------------------------------------
def parse_hotkey(sequence: str) -> Tuple[int, str]:
    """
    Split a hotkey string such as ``"Alt+Shift+S"``.

    Returns the XCB modifier mask and the key name.

    Raises
    ------
    ValueError
        If the sequence is empty, contains an empty token, has more than one
        non-modifier key, or lists no key at all.
    """
    modifiers = 0
    key: Optional[str] = None
    for raw in sequence.split("+"):
        token = raw.strip()
        if not token:
            raise ValueError("Empty token")
        if token in MODIFIER_MAP:
            modifiers |= MODIFIER_MAP[token]
        elif key is None:
            key = token
        else:
            raise ValueError("Multiple key names")
    if key is None:
        raise ValueError("No key name")
    return modifiers, key


def format_hotkey(modifiers: Iterable[str], key: str) -> str:
    """
    Build a canonical sequence string from modifiers and a key name.
    """
    present = set(modifiers)
    ordered = [m for m in MODIFIER_ORDER if m in present]
    return "+".join(ordered + [key])


def diff_hotkeys(
    hotkeys: Dict[str, str], baseline: Optional[Dict[str, str]] = None
) -> Dict[str, str]:
    """
    Return only the entries of *hotkeys* that differ from *baseline*.

    ``baseline`` defaults to :data:`DEFAULT_HOTKEYS`, matching the top-level
    YAML use. Callers diffing a profile against a global baseline pass the
    baseline's own hotkeys mapping.
    """
    base = baseline if baseline is not None else DEFAULT_HOTKEYS
    return {k: v for k, v in hotkeys.items() if base.get(k) != v}
