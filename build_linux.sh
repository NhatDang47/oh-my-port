#!/usr/bin/env bash
# Build script for Linux
# Run from the project root:
#   chmod +x build_linux.sh && ./build_linux.sh
#
# Prerequisites on Linux:
#   pip install uv  (or: curl -LsSf https://astral.sh/uv/install.sh | sh)
#   uv sync

set -e

echo "🚀 Building oh-my-port for Linux..."

uv run pyinstaller oh-my-port.spec \
    --distpath dist/linux \
    --workpath build/linux \
    --noconfirm

BINARY="dist/linux/oh-my-port"

if [ -f "$BINARY" ]; then
    chmod +x "$BINARY"
    SIZE=$(du -sh "$BINARY" | cut -f1)
    echo ""
    echo "✅ Build successful!"
    echo "   Output: $BINARY"
    echo "   Size:   $SIZE"
else
    echo "❌ Build failed. Check the output above for errors."
    exit 1
fi
