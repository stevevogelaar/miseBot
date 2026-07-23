# miseBot — Autonomous Kitchen Agent

## Problem

Restaurant kitchens waste hours every day on manual list management:
- Paper prep lists get covered in food and lost
- Shopping lists are forgotten in pockets
- Staff run out of stock mid-service because no one tracked usage
- Communication to suppliers is manual and error-prone

**Brianne at 106 Wigle** spends 30+ minutes each morning writing prep lists, checking stock, and texting suppliers. She's running a kitchen, not a spreadsheet.

## Solution

**miseBot** — an AI agent that lives in your kitchen and thinks ahead.

Instead of just recording what you tell it, miseBot:
- **Predicts** what you'll need based on tonight's menu
- **Monitors** stock levels and warns before you run out
- **Orchestrates** your day — prep, lunch, setup, service
- **Drafts** emails so you just hit send

All via natural language. "Add tomatoes to shopping" → done. "I finished whipped feta" → marked. "Email my prep list to Kyle" → sent.

## How It Works

### Architecture

```
User (text/voice)
    ↓
Gemma 4 (Ollama local) — intent classification, entity extraction
    ↓
miseBot Engine — action router
    ↓
SQLite — persistent lists, ingredients, schedule
    ↓
Streamlit UI — phone-optimized, real-time updates
```

### Key Autonomy Features

| Feature | What It Does | Why It's Autonomous |
|---------|-------------|---------------------|
| **Smart Prep** | Select tonight's menu → auto-populates prep list | Agent initiates work from a plan |
| **Auto-Replenish** | Tracks usage rates, suggests reorder when stock < 3 days | Agent acts before human notices problem |
| **Day Keeper** | Builds schedule, monitors actual vs. planned pace, auto-adjusts | Agent manages time, not just records it |
| **Proactive Reminders** | "Pull rice at 3pm" → appears in timeline, turns red when elapsed | Agent surfaces alerts without being asked |

### Demo Flow (2 minutes)

1. **Open app** — phone-shaped UI, logo, tagline
2. **Set menu** — select "Whipped Feta Burger, Smash Burger"
3. **Watch auto-prep** — 8 prep items appear instantly
4. **Check smart suggestions** — "Coffee: 1 bag left, 2 days remaining. Add to list?"
5. **Talk to bot** — "Prep till noon, lunch half hour, dinner setup at 5"
6. **See timeline** — vertical blocks: prep → lunch → setup → service
7. **Mark items done** — check off 8 prep items, confetti at 100%
8. **Email list** — one-click, formatted HTML table with checkboxes

### Technical Decisions

**Why Streamlit + not React?**
- 2-day build deadline. Streamlit = Python-only, zero frontend framework setup.
- Mobile-first via CSS phone frame. Looks like a native app on desktop demo.

**Why SQLite + not cloud DB?**
- Local-first = works offline, zero hosting costs, instant setup.
- Persistent across sessions. Lists survive browser close.

**Why Gemma 4 + not OpenAI?**
- Hackathon requires Gemma integration.
- Local via Ollama = total privacy, no API costs, works without internet.
- Fallback rule-based parser ensures app works even if Ollama is offline.

**Why email + not supplier API?**
- Every supplier has email. Zero integration overhead.
- Prep list email includes checkbox column → print and check off.

## Challenges & How We Solved Them

| Challenge | Solution |
|-----------|----------|
| 2-day deadline | Scope ruthlessly: lists + autonomy features only. No recipe scaling, no POS integration. |
| Gemma local can be slow | Fallback rule-based parser handles 90% of commands instantly. Gemma only for edge cases. |
| Mobile UI in Streamlit | Custom CSS phone frame, 375px max-width, touch-friendly buttons. |
| Real restaurant data privacy | Seeded 25 generic ingredients + 28 prep items. No actual vendor names or costs exposed. |
| Demonstrating autonomy in a demo | Pre-seed low-stock items (coffee at 1 bag) so auto-replenish triggers immediately. |

## What's Next

### Immediate (v0.2)
- Voice input via browser Web Speech API
- Recipe scaling: "50 covers → how many buns?"
- Supplier API integration (Sysco, Gordon Food Service)
- Multi-location: Brianne manages 106 Wigle + future locations
- Telegram bot: text miseBot from the line without opening the app

### Autonomy Graduation (v0.3)
miseBot implements a **risk-tiered autonomy model** inspired by production self-healing agents:

**Phase 1: Observe-Only (Week 1)**
- miseBot detects low-stock, prep gaps, schedule conflicts
- Suggests actions but requires one-tap approval
- Logs every suggestion with accuracy score

**Phase 2: Trusted Auto-Actions (Week 2+)**
- Auto-replenish when accuracy > 95% for that ingredient
- Auto-prep suggestions when menu-to-prep mapping is stable
- Day Keeper turns yellow → red warnings without auto-deleting items

**Phase 3: Full Autonomy (Month 1)**
- Email lists auto-send to verified supplier addresses
- Prep lists auto-generate at 6 AM based on calendar + reservations
- Anomaly detection: "You usually order 5 lbs tomatoes on Thursday. It's Thursday and you have 2 lbs."

**Safety Guardrails (Always On):**
- **Deduplication:** Same error/warning won't trigger twice in 1 hour
- **Rate limiting:** Max 20 auto-actions per shift
- **Restart throttle:** 3 auto-restarts per feature per day, then human required
- **Kill switch:** "Stop auto" in Settings disables all autonomy instantly
- **Fallback parser:** If Gemma goes offline, rule-based NLU handles 90% of commands

### Infrastructure Parity
miseBot shares HAL's philosophy: autonomous agents don't replace human judgment — they earn trust through observation, then act within bounded safety. Every auto-action is reversible, logged, and can be inspected.

## Project Links

- **Repository:** https://github.com/stevevogelaar/miseBot.git
- **Live Demo:** (coming soon)
- **Video:** (coming soon)

---

*Built by Steve Vogelaar + HAL for the GDG Windsor Gemma Hackathon, July 24 2026.*
