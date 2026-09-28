#!/bin/bash
set -e
APP_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$APP_DIR"

echo ""
echo "SOKINIHMWWWEIMWEI - ONE-TIME SETUP"
echo "======================================"
echo ""

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python is not installed. Installing it..."
  sudo apt-get update
  sudo apt-get install -y python3
fi

if [ ! -f .env ] || ! grep -q '^OPENAI_API_KEY=' .env 2>/dev/null; then
  echo "Paste your OpenAI API key below. It will be saved only on this Chromebook."
  printf "OpenAI API key: "
  read -r OPENAI_KEY
  if [ -z "$OPENAI_KEY" ]; then
    echo "No key entered. Setup cancelled."
    exit 1
  fi
  printf 'OPENAI_API_KEY=%s\nOPENAI_MODEL=gpt-5.6-luna\nPORT=8787\n' "$OPENAI_KEY" > .env
  chmod 600 .env
else
  echo "OpenAI key already configured. Keeping it."
fi

chmod +x start.sh stop.sh server.py
mkdir -p "$HOME/.local/share/applications"
cat > "$HOME/.local/share/applications/sokinihmwweimwei.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Sokinihmwweimwei
Comment=OpenAI Lesson Generator
Exec=/bin/bash -lc 'cd "$APP_DIR" && ./start.sh'
Icon=web-browser
Terminal=false
Categories=Education;
EOF

echo ""
echo "Setup complete."
echo "Look in your Chromebook Launcher for: Sokinihmwweimwei"
echo ""
echo "If it does not appear immediately, sign out/in or restart the Linux environment."
echo ""
