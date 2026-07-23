# miseBot

**Your AI Sous-Chef. Prep smarter. Order faster. Never miss a beat.**

miseBot is an autonomous kitchen agent that manages prep lists, shopping lists, and daily schedules for restaurant and café kitchens. Built for the [GDG Windsor - Build with AI - Gemma Hackathon](https://www.kaggle.com/competitions/build-with-gemma-gdg-windsor), July 2026.

---

## 🎬 Demo

*Coming soon — screen recording and live demo link.*

## 🚀 Quick Start

```powershell
cd "C:\Users\Steve Vogelaar\Documents\_IT Oversight\Hackathon\miseBot"
# Windows
Start-miseBot.bat

# Or manually
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Open browser to `http://localhost:8501`

## 🧠 What It Does

- **Two Lists:** Shopping list + Prep list, persistent and editable
- **Natural Language:** "Add tomatoes to shopping" / "I finished whipped feta" / "Email my prep list to Kyle"
- **Smart Prep:** Select tonight's menu → auto-generates prep items
- **Auto-Replenish:** Tracks usage rates, warns when stock is low, suggests reorder
- **Day Keeper:** Builds a timeline from your schedule, monitors pace, warns if behind
- **Reminders:** "Pull rice at 3pm" → appears in timeline, turns red when elapsed
- **Email:** One-click send lists as formatted HTML tables (prep includes checkboxes)
- **Confetti:** When all prep is done 🎉

## 🏗️ Architecture

| Layer | Tech |
|-------|------|
| UI | Streamlit (mobile-first, phone frame CSS) |
| Brain | Google Gemma 4 via Ollama local HTTP API |
| Memory | SQLite (lists, items, ingredients, settings, timeline) |
| Comms | Python smtplib (HTML email) |

## 📁 Structure

```
miseBot/
├── app.py                  # Main Streamlit app
├── database.py             # SQLite CRUD layer
├── bot_engine.py           # Gemma 4 NLU parser + fallback
├── email_sender.py         # HTML email builder + SMTP sender
├── data/
│   └── seed_data.py        # 25 ingredients + 28 prep items + 7 menu items
├── components/
│   └── mobile_frame.py     # CSS phone frame, animations, timeline styles
├── utils/
│   └── helpers.py          # Quantity parsing, time conversion, stock math
├── Start-miseBot.bat       # One-click launcher
├── requirements.txt
└── miseBot-logo.png
```

## 🗃️ Database Schema

- `lists` — shopping / prep lists with TTL
- `list_items` — items with quantity, unit, status
- `ingredients` — seeded from 106 Wigle RC data (usage rates, stock levels)
- `menu_items` — signature dishes with linked prep items
- `time_blocks` — Day Keeper schedule
- `reminders` — time-based alerts
- `settings` — email, TTL, active user

## 🎯 Hackathon Track

**Track 2: Autonomous Agent**

Autonomy features that qualify:
1. **Smart Prep from Menu** — auto-generates prep list from selected dishes
2. **Auto-Replenish** — monitors stock depletion, proactively suggests reorder
3. **Day Keeper** — builds timeline, monitors pace, auto-adjusts when behind
4. **Proactive Reminders** — queued alerts surfaced in timeline

## 📝 Kaggle Writeup

See `docs/HACKATHON_WRITEUP.md` for full competition writeup.

## ⚙️ Configuration

Click ⚙️ gear icon in app to set:
- Email to / from addresses
- SMTP host/port/credentials
- List TTL (1–30 days)
- Active user name

## 🤝 Credits

- Built by Steve Vogelaar + HAL (AI collaborator)
- Gemma 4 via Ollama for local LLM reasoning
- Inspired by 106 Wigle kitchen operations

## 📜 License

MIT
