#!/bin/sh

# Configuration
APP_NAME="io.github.baronsmv.linux-rt-upscaler"
DATA_URL="https://raw.githubusercontent.com/baronsmv/linux-rt-upscaler/refs/heads/main/data"
DATA_DIR="$HOME/.local/share"

DESKTOP_PATH="applications"
DESKTOP_URL="$DATA_URL/$DESKTOP_PATH/$APP_NAME.desktop"
DESKTOP_DIR="$DATA_DIR/$DESKTOP_PATH"
DESKTOP_FILE="$DESKTOP_DIR/$APP_NAME.desktop"

ICON_PATH="icons/hicolor/256x256/apps"
ICON_URL="$DATA_URL/$ICON_PATH/$APP_NAME.png"
ICON_DIR="$DATA_DIR/$ICON_PATH"
ICON_FILE="$ICON_DIR/$APP_NAME.png"

# Binary location
CMD_PATH="$HOME/.local/bin/upscale-gui"
if command -v upscale-gui >/dev/null 2>&1; then
    # Custom location
    CMD_PATH=$(command -v upscale-gui)
fi
if [ ! -x "$CMD_PATH" ]; then
    echo "Error: 'upscale-gui' not found at $CMD_PATH" >&2
    exit 1
fi
echo "Using executable: '$CMD_PATH'"

# Directories creation
echo "Creating desktop and icon directories if needed..."
mkdir -p "$DESKTOP_DIR" "$ICON_DIR"

# Icon file
echo "Downloading icon file..."
curl -fsSL "$ICON_URL" -o "$ICON_FILE"
chmod 644 "$ICON_FILE"

# Desktop file
echo "Downloading desktop file..."
# Download to temp before edit
TMP_DESKTOP=$(mktemp)
curl -fsSL "$DESKTOP_URL" -o "$TMP_DESKTOP"
# Replace binary placeholder
sed -i "s|EXEC_PATH_PLACEHOLDER|$CMD_PATH|g" "$TMP_DESKTOP"
# Move temp
mv "$TMP_DESKTOP" "$DESKTOP_FILE"
chmod 644 "$DESKTOP_FILE"

echo "Installation complete."
echo "Desktop file: '$DESKTOP_FILE'"
echo "Icon file: '$ICON_FILE'"