IT Ticket Log App (Streamlit)
=============================
- Admin view: full tracker with Add Ticket, Table, and Summary tabs.
- Public view: submit-only page (use URL: http://<host>:8501/?mode=submit).
- Monthly cap default: 8 (change in sidebar).

Running on macOS
----------------
1) Open Terminal, cd to this folder.
2) python3 -m venv .venv
3) source .venv/bin/activate
4) pip install -r requirements.txt
5) Admin view:   python -m streamlit run app.py
6) Public (LAN): python -m streamlit run app.py --server.address=0.0.0.0 --server.port=8501
   Then share: http://<your-mac-ip>:8501/?mode=submit
