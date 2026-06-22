#!/usr/bin/env bash
# deploy_openclaw_aivan.sh — run this ON the server (root@113.249.119.30)
# Completes the OpenClaw → AIVAN integration after git pull.
set -euo pipefail

REPO_DIR="/opt/giraffe/giraffe-agent"
PLUGIN_SRC="$REPO_DIR/integrations/openclaw-aivan-plugin"
AIVAN_BASE="http://localhost:8000"

echo "=== [1/7] Pull latest code ==="
cd "$REPO_DIR"
git fetch origin
git checkout claude/openclaw-aivan-integration-35qace
git pull origin claude/openclaw-aivan-integration-35qace

echo "=== [2/7] Build OpenClaw plugin ==="
cd "$PLUGIN_SRC"
npm install
npx tsc
echo "Plugin compiled: dist/index.js"

echo "=== [3/7] Install plugin into OpenClaw ==="
openclaw plugins install "$PLUGIN_SRC"
openclaw plugins list | grep -i aivan && echo "Plugin visible in list" || echo "WARNING: plugin not in list"

echo "=== [4/7] Configure systemd env override for Gateway ==="
mkdir -p ~/.config/systemd/user/openclaw-gateway.service.d
cat > ~/.config/systemd/user/openclaw-gateway.service.d/env.conf << 'ENVEOF'
[Service]
Environment="AIVAN_BASE_URL=http://localhost:8000"
Environment="GIRAFFE_API_BASE=http://localhost:8000"
ENVEOF
echo "Gateway env override written."

echo "=== [5/7] Create AIVAN systemd service ==="
cat > ~/.config/systemd/user/aivan.service << 'SVCEOF'
[Unit]
Description=AIVAN Procurement AI Service
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/giraffe/giraffe-agent
Environment="GIRAFFE_DB_MODE=off"
ExecStart=/opt/giraffe/giraffe-agent/.venv/bin/uvicorn api.main:app --host 127.0.0.1 --port 8000
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
SVCEOF

systemctl --user daemon-reload
systemctl --user enable --now aivan.service
sleep 3
systemctl --user status aivan.service --no-pager || true

echo "=== [6/7] Enable plugin and restart Gateway ==="
openclaw config set plugins.entries.openclaw-aivan.enabled true
systemctl --user daemon-reload
openclaw gateway restart || systemctl --user restart openclaw-gateway.service
sleep 3

echo "=== [7/7] Verify ==="
echo "--- Health check ---"
curl -s http://localhost:8000/health

echo ""
echo "--- Plugin list ---"
openclaw plugins list | grep -i aivan || echo "(not found)"

echo ""
echo "--- Channel status ---"
openclaw channels status --probe || true

echo ""
echo "--- Gateway logs (last 20 lines, grep aivan) ---"
journalctl --user -u openclaw-gateway.service -n 50 --no-pager | grep -i aivan || echo "(no aivan logs yet)"

echo ""
echo "=== Deploy complete ==="
echo "Next: send a real WeChat message and check for RFQ-XXXXXXXX response."
