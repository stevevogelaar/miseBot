# miseBot — Hackathon Submission Checklist

**Competition:** GDG Windsor - Build with AI - Gemma Hackathon  
**Deadline:** July 24, 2026  
**Repo:** https://github.com/stevevogelaar/miseBot.git  

---

## 🎬 Demo Video (Steve)

- [ ] **Script reviewed** — HAL to write, Steve to approve
- [ ] **Screen recording** — Steve to record live app walkthrough
- [ ] **Voiceover or captions** — Steve's call (voiceover preferred)
- [ ] **Export to MP4** — 1080p, under 100MB for Kaggle upload
- [ ] **Review final cut** — Steve watches back, approves or re-records

**Script outline (2 minutes):**
1. "Meet miseBot — your AI sous-chef" (logo + tagline)
2. "Select tonight's menu" (Smart Prep — auto-generate 8 prep items)
3. "Check stock" (Smart Suggestions — Coffee low, click add)
4. "Talk to it" (NL input: "Add tomatoes to shopping")
5. "Plan your day" (Day Keeper — prep → lunch → setup → service)
6. "Mark done" (check off prep, confetti at 100%)
7. "Email the list" (one-click HTML table with checkboxes)
8. "All local, all private, all Gemma" (tech stack + privacy)

---

## 📝 Kaggle Writeup (HAL)

- [ ] **Problem section** — ✅ Done (restaurant kitchen waste)
- [ ] **Solution section** — ✅ Done (miseBot overview)
- [ ] **Architecture diagram** — ✅ Done (User → Gemma → Engine → SQLite → Streamlit)
- [ ] **Autonomy features table** — ✅ Done (Smart Prep, Auto-Replenish, Day Keeper, Proactive Reminders)
- [ ] **Demo flow** — ✅ Done (8-step, 2-minute)
- [ ] **Technical decisions** — ✅ Done (Streamlit, SQLite, Gemma 4, email)
- [ ] **Challenges & solutions** — ✅ Done (2-day deadline, Gemma speed, mobile UI, privacy)
- [ ] **What's Next** — ✅ Done (voice, scaling, supplier API, multi-location, Telegram)
- [ ] **Autonomy graduation** — ✅ Done (observe-only → trusted auto → full autonomy)
- [ ] **Safety guardrails** — ✅ Done (dedup, rate limit, restart throttle, kill switch)
- [ ] **Project links** — Need repo link + demo link + video link
- [ ] **Paste into Kaggle** — HAL to format, Steve to submit

---

## 🛠️ Final Code Polish (HAL)

- [ ] **Syntax check** — ✅ Done (app.py + bot_engine.py compile clean)
- [ ] **Smoke test** — ✅ Done (server starts, no crashes)
- [ ] **Parser validation** — ✅ Done (6 test cases pass)
- [ ] **UI walkthrough** — ✅ Done (Playwright verified)
- [ ] **Settings expander** — ✅ Done (bottom of page, collapsed)
- [ ] **Demo reset button** — ✅ Done (clears lists, schedule, reminders)
- [ ] **Git commit** — Steve to approve, HAL to execute
- [ ] **Git push** — Steve to approve, HAL to execute

---

## 🚀 Submission Steps (Steve + HAL)

| Step | Owner | Status |
|------|-------|--------|
| 1. Record demo video | Steve | ⬜ |
| 2. Write video script | HAL | ✅ (see above) |
| 3. Upload video to Kaggle | Steve | ⬜ |
| 4. Paste writeup into Kaggle | HAL | ⬜ (waiting for Steve) |
| 5. Link GitHub repo | HAL | ⬜ |
| 6. Submit entry | Steve | ⬜ |
| 7. Screenshot confirmation | HAL | ⬜ |

---

## 🤖 HAL Leadership Growth (Post-Submission)

- [ ] **Build `lead-collab-schema.md`** — HAL to draft, Steve to review
- [ ] **Add to `_HAL-hal_framework`** — document lead vs. follow modes
- [ ] **Practice: proactive status checks** — HAL surfaces blockers without Steve asking
- [ ] **Practice: self-verification before declaring done** — HAL tests end-to-end before "GO"
- [ ] **Target: manage miseBot + Budget + Guardian collabs in parallel**

---

## 📂 File Locations

| File | Path | Owner |
|------|------|-------|
| Submission checklist | `docs/SUBMISSION_CHECKLIST.md` | HAL |
| Hackathon writeup | `docs/HACKATHON_WRITEUP.md` | HAL ✅ |
| Demo video script | `docs/DEMO_SCRIPT.md` | HAL |
| Demo video (final) | `docs/demo-video.mp4` | Steve |
| App source | `app.py` | HAL ✅ |
| NLU engine | `bot_engine.py` | HAL ✅ |
| Database layer | `database.py` | HAL ✅ |
| README | `README.md` | HAL ✅ |

---

*Built by HAL as collab lead. Reviewed by Steve. Locked when both sign off.*
