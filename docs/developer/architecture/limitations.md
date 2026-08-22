# Architecture Limitations

## Native Wayland is not supported

Native Wayland capture and input forwarding are **not planned** for the foreseeable future.

### Why?

[Wayland's security model](https://docs.getwayland.com/core/security-model/) isolates applications from each other. This imposes two main challenges for the current architecture:

1. At **capture** level. A Wayland client cannot read pixels from another client without compositor-specific protocols such as [PipeWire](https://www.pipewire.org/). These protocols vary between KWin, Mutter, wlroots and others, making the capture implementation non-agnostic.
2. At **event-forward** level. Wayland does not allow synthetic mouse events to be sent to other windows. This is a core X11 feature of the upscaler that has currently **no equivalent in Wayland** unless [explicitly disabling Wayland restrictions](https://mouseless.click/docs/wayland_configuration.html), which would require user intervention and may introduce unnecessary security vulnerabilities.

The latter is especially problematic. While applications like [OBS Studio](https://feaneron.com/2021/03/30/obs-studio-on-wayland/) managed to cleanly overcome the first challenge, that cannot be said about the second one. Alternatives to XTest (which is the closest thing to X11 synthetic events), like [uinput](https://www.kernel.org/doc/html/v4.12/input/uinput.html), [ydotool](https://github.com/ReimuNotMoe/ydotool) and [wdotool](https://github.com/cushycush/wdotool) exist, but they introduce cursor-warp artifacts for every mouse event (like XTest does) and may not even work across all compositors, as suggested by wdotool developers:

> If you've been wanting xdotool on Wayland, this is the closest thing. [...] "Closest thing" is doing real work in that sentence. [...]

> For comparison with the alternatives: xdotool is X11-only and does not work on Wayland at all. ydotool writes to /dev/uinput, which means root (or carefully tuned udev rules), no focus awareness, and no window management. It bypasses the compositor entirely, which breaks inside sandboxed sessions and loses any security boundary the compositor was enforcing. [...]

Therefore, supporting native Wayland would require:

- Per-compositor capture backends, involving PipeWire integration with every step of the pipeline.
- A completely different overlay/input approach (likely compositor-specific, similar to [Gamescope](https://github.com/ValveSoftware/gamescope) which is a compositor itself).

This does not fit the current XShm/XDamage architecture and would add significant maintenance complexity for a relatively small use case (most games can run on XWayland, which is supported).

### What works on Wayland sessions?

The upscaler works on Wayland sessions **only through XWayland**. If an application runs natively under Wayland (not XWayland), **it cannot be captured or controlled by the upscaler**.

X11 provides:

- `XShm` / `XDamage` for efficient window capture, also making tile-based processing possible.
- Global mouse/keyboard hooks for input forwarding, without artificial cursor jumping (like XTest does).
- Consistent behavior across desktop environments (instead of compositor-specific behavior).

These are the foundations of the current capture and overlay pipeline.
