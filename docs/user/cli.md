# Command-Line Interface (CLI)

## Target selection

With the `upscale` command, you can target windows using different options:

- Upscaling the currently active windows (after a 5-sec wait):
  ```bash
  upscale
  ```

- Selecting it interactively from a list:
  ```bash
  upscale -s
  ```

- By matching its name:

    - Using a substring:
    ```bash
    upscale -t firefox
    ```

    - Or a regular expression:
    ```bash
    upscale --target-title-regex "(Yuzu|Ryujinx).*"
    ```

- By starting in daemon mode:
  ```bash
  upscale -d
  ```

- Launching and upscaling it (although not as reliable as the other options):
  ```bash
  upscale -- program-to-lauch --some-flag
  ```

## Basic Options

With the CLI options, you can:

- Define which SRCNN model to use:
  ```bash
  upscale -m 4x24
  ```

- Upscale to 4x (e.g., 720p to 2880p, then adjust to screen), using two consecutive 2x passes:
  ```bash
  upscale -2
  ```

- Upscale any valid window when focusing it, instead of locking to the first upscaled window:
  ```bash
  upscale -f
  ```

- Stretch the upscaled window to cover the entire screen, ignoring its aspect ratio:
  ```bash
  upscale -o stretch
  ```

- Crop one or more sides of the upscaled window (e.g., 29px from the top and 3 from each other side):
  ```bash
  upscale --crop-top 29 --crop-bottom 3 --crop-left 3 --crop-right 3
  ```

Any option can be combined with others.

For more common options, use `upscale -h`. Alternatively you can use `upscale --help-all` to see every option including advanced ones.
