# 📊 Props Sports Dashboard

A dual-sport (MLB + NBA) props dashboard inspired by Props.Cash — with login, paid subscription control, streaks, hit rate analysis, and visualizations.

## Features
- 🔐 Secure login (demo / password123)
- 🧾 Paid subscription control (only paid users can download or access premium features)
- ⚾ MLB Statcast analytics with barrel/total bases tracking
- 🏀 NBA player game logs with prop tracking
- Color-coded hit rates, streaks, and average difference from line

## How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy
Deploy to [Streamlit Cloud](https://streamlit.io/cloud) — upload `config.yaml` and `paid_users.json` as secret files if needed.
