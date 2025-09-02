
#!/bin/bash
APP_DIR="$(cd "$(dirname "$0")"/.. && pwd)"
cd "$APP_DIR" || exit 1
if [ ! -d ".venv" ]; then /usr/bin/python3 -m venv .venv; fi
source .venv/bin/activate
pip install --upgrade pip >/dev/null 2>&1
pip install -r requirements.txt >/dev/null 2>&1
IP=$(ipconfig getifaddr en0 2>/dev/null); if [ -z "$IP" ]; then IP=$(ipconfig getifaddr en1 2>/dev/null); fi
echo "Share this link on your Wi‑Fi/LAN: http://$IP:8501/?mode=submit"
python -m streamlit run app.py --server.address=0.0.0.0 --server.port=8501 --server.headless=true
