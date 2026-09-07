# Watershed Intelligence Backend
FastAPI + SQLite backend for Problem Statement 26015.

Run:
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python seed.py
uvicorn main:app --reload

Docs: http://127.0.0.1:8000/docs
APIs: /images, /watersheds, /interventions, /analysis, /change
