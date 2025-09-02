
#!/bin/bash
APP_DIR="$(cd "$(dirname "$0")"/.. && pwd)"
cd "$APP_DIR" || exit 1
if [ ! -d ".venv" ]; then /usr/bin/python3 -m venv .venv; fi
source .venv/bin/activate
pip install --upgrade pip >/dev/null 2>&1
pip install -r requirements.txt >/dev/null 2>&1
python -m streamlit run app.py --server.headless=true
