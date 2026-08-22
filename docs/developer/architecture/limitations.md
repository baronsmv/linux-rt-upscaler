# Architecture Limitations

## Native Wayland is not supported

Native Wayland capture and input forwarding are **not planned** for the foreseeable future.

### Why?

[Wayland's security model](https://docs.getwayland.com/core/security-model/) isolates applications from each other by design. This creates two hard problems for the current upscaler architecture:

1. **Capture**: A Wayland client cannot read pixels from another client directly, it must use the portal/PipeWire capture path. While this is the standard solution used by [OBS Studio](https://feaneron.com/2021/03/30/obs-studio-on-wayland/) and others, it adds a completely separate capture pipeline and may behave differently across portal implementations and compositors.
2. **Event forwarding**: Wayland has no equivalent to X11 synthetic event delivery. An external client cannot send mouse events directly to a specific surface without moving the real system pointer. Tools based on `uinput`, virtual pointer protocols, or the RemoteDesktop portal can inject input, but they all move the real cursor, warping it to the target coordinates. This is fundamentally different from the current X11 forwarder, which sends synthetic events without moving the cursor.

The second problem is especially limiting. Alternatives such as [ydotool](https://github.com/ReimuNotMoe/ydotool) and [wdotool](https://github.com/cushycush/wdotool) can inject real input events on Wayland, but they require the pointer to move to the target window's position. This introduces cursor-warp artifacts and loses the direct behavior the upscaler relies on.

As the wdotool developers put it:

> If you've been wanting xdotool on Wayland, this is the closest thing. [...] "Closest thing" is doing real work in that sentence. [...]

> For comparison with the alternatives: xdotool is X11-only and does not work on Wayland at all. ydotool writes to /dev/uinput, which means root (or carefully tuned udev rules), no focus awareness, and no window management. It bypasses the compositor entirely, which breaks inside sandboxed sessions and loses any security boundary the compositor was enforcing. [...]

Supporting native Wayland would therefore require:

- A separate capture backend based on xdg-desktop-portal/PipeWire.
- A completely different input strategy, most likely moving the real system pointer via `uinput` or another virtual input mechanism, or becoming a compositor-integrated tool.

This does not fit the current XShm/XDamage architecture and would add significant maintenance complexity for a relatively small use case, since most games and visual novels already run through XWayland.

### What works on Wayland sessions?

The upscaler works on Wayland sessions **only through XWayland**.

If an application runs natively under Wayland (not XWayland), **it cannot be captured or controlled by the upscaler**.

X11 provides the foundations the current pipeline depends on:

- `XShm` / `XDamage` for efficient window capture, including tile-based processing.
- Global mouse and keyboard hooks for input forwarding without artificial cursor movement.
- Consistent behavior across desktop environments.

These are not available under native Wayland without a substantially different architecture.

[](limitations.md#native-wayland-is-not-supported)