"""miseBot — Autonomous Kitchen Agent for Smart Prep, Shopping, and Day Orchestration."""
import streamlit as st
import random
from datetime import datetime, timedelta

from database import (
    init_db,
    get_or_create_list,
    add_item,
    get_items,
    mark_done,
    mark_pending,
    remove_item,
    get_settings,
    save_settings,
    get_ingredients,
    get_menu_items,
    add_time_block,
    get_time_blocks,
    add_reminder,
    get_reminders,
    dismiss_reminder,
    record_suggestion,
    get_ingredient_stats,
    get_auto_actions,
    log_auto_action,
    is_deduplicate,
    check_rate_limit,
    check_restart_throttle,
    reset_safety_counters,
    increment_safety_counter,
)
from data.seed_data import run_seed
from bot_engine import parse_user_input, generate_reply
from email_sender import build_shopping_email, build_prep_email, send_email
from components.mobile_frame import inject_mobile_css
from components.logo_b64 import LOGO_B64
from utils.helpers import check_low_stock

# ─── Autonomy helpers ─────────────────────────────────────────────────────────
import hashlib

def _log_hash(text: str) -> str:
    return hashlib.md5(text[-200:].encode("utf-8")).hexdigest()[:16]

def get_autonomy_phase(ing_name: str, min_confidence: float = 0.95, min_approvals: int = 5) -> str:
    """Returns: observe_only | trusted_auto | full"""
    stats = get_ingredient_stats(ing_name)
    if not stats:
        return "observe_only"
    acc = stats.get("accuracy_score", 0.0)
    approvals = stats.get("approval_count", 0)
    if acc >= min_confidence and approvals >= min_approvals:
        return "trusted_auto"
    return "observe_only"

def get_auto_setting(key: str, default=True):
    s = get_settings()
    return s.get(key, default)

def set_auto_setting(**kwargs):
    save_settings(**kwargs)

def _is_valid_item(name: str) -> bool:
    """Reject garbage from fallback parser."""
    if len(name) > 30 or len(name) < 2:
        return False
    garbage = {"before", "tonight", "dinner", "service", "make", "want", "going", "will", "should", "could", "would"}
    words = name.lower().split()
    if any(w in garbage for w in words):
        return False
    return True

# ─── Init ────────────────────────────────────────────────────────────────────
init_db()
if "seeded" not in st.session_state:
    run_seed()
    st.session_state.seeded = True

# Reset safety counters if new day
reset_safety_counters()

st.set_page_config(page_title="miseBot", page_icon="🍳", layout="centered")
inject_mobile_css()

# ─── Session State ───────────────────────────────────────────────────────────
defaults = {
    "chat_log": [],
    "active_tab": "prep",
    "prep_collapsed": False,
    "shopping_collapsed": False,
    "demo_menu_set": False,
    "demo_day_set": False,
    "confetti_fired": False,
    "last_chat_input": "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── Settings ────────────────────────────────────────────────────────────────
settings = get_settings()

# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; margin-bottom:12px;">
        <img src="data:image/png;base64,{LOGO_B64}" alt="miseBot" style="width:200px; height:200px; border-radius:16px; margin-bottom:4px;">
        <span style="font-size:24px; font-weight:700; color:#1A1A1A;">miseBot</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─── Smart Suggestions (Autonomous) ──────────────────────────────────────────
ingredients = get_ingredients()
low_stock_alerts = []
for ing in ingredients:
    if ing.get("current_stock") is not None and ing.get("min_stock") is not None and ing.get("usage_rate_per_week"):
        days = check_low_stock(ing["current_stock"], ing["min_stock"], ing["usage_rate_per_week"])
        if days is not None and days <= 3:
            low_stock_alerts.append(
                {"name": ing["name"], "days": days, "stock": ing["current_stock"],
                 "text": f"{ing['name']} — {days} days left (stock: {ing['current_stock']})"}
            )

auto_enabled = get_auto_setting("auto_enabled", True)
max_actions = int(get_auto_setting("max_auto_actions", 20))
max_restarts = int(get_auto_setting("max_restarts", 3))

if low_stock_alerts:
    st.markdown("<div style='margin:8px 0;'><b>🔔 Smart Suggestions</b></div>", unsafe_allow_html=True)
    for alert in low_stock_alerts[:3]:
        name = alert["name"]
        phase = get_autonomy_phase(name)
        log_h = _log_hash(alert["text"])

        # Guardrails
        if is_deduplicate(log_h, hours=1):
            continue
        if not check_rate_limit(max_actions):
            st.caption("⚠️ Rate limit reached. No more auto-actions this shift.")
            break

        if phase == "trusted_auto" and auto_enabled:
            # AUTONOMOUS: add directly
            lst = get_or_create_list("shopping")
            add_item(lst["id"], name, "1", "ea")
            log_auto_action(
                action_type="auto_replenish",
                target=name,
                trigger_reason=f"{alert['days']} days stock remaining",
                result="added_to_shopping",
                user_approved=True,
                confidence=alert.get("confidence", 0.95),
                log_hash=log_h,
            )
            increment_safety_counter("auto_action_count")
            record_suggestion(name, approved=True, confidence=0.95)
            # Mark dedup so this doesn't re-fire
            log_auto_action(
                action_type="dedup_marker",
                target=name,
                log_hash=log_h,
            )
            st.toast(f"🤖 Auto-added {name} to shopping list")
            st.rerun()
        else:
            # OBSERVE-ONLY: show suggest button
            if st.button(f"➕ {alert['text']}", key=f"alert_{name[:20]}"):
                lst = get_or_create_list("shopping")
                add_item(lst["id"], name, "1", "ea")
                log_auto_action(
                    action_type="suggest_replenish",
                    target=name,
                    trigger_reason=f"{alert['days']} days stock remaining",
                    result="user_approved_added",
                    user_approved=True,
                    confidence=0.6,
                    log_hash=log_h,
                )
                # Mark dedup only AFTER click so button re-appears next load
                log_auto_action(
                    action_type="dedup_marker",
                    target=name,
                    log_hash=log_h,
                )
                record_suggestion(name, approved=True, confidence=0.6)
                st.toast(f"Added {name} to shopping list")
                st.rerun()

# ─── Chat Input ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin: 8px 0;">
    <small style="color:#555555;">Tell me your day... Try: "Add tomatoes to shopping" or "I finished whipped feta"</small>
</div>
""", unsafe_allow_html=True)

# Dark-border CSS for prompt box
st.markdown("""
<style>
[data-testid="stTextInput"] input {
    border: 2px solid #1A1A1A !important;
    border-radius: 8px !important;
    padding: 8px 12px !important;
}
</style>
""", unsafe_allow_html=True)

with st.form(key="chat_form", clear_on_submit=True):
    cols = st.columns([5, 1])
    with cols[0]:
        chat_input = st.text_input("", placeholder="Type a command...", label_visibility="collapsed")
    with cols[1]:
        submit = st.form_submit_button("⤶", use_container_width=True)

if submit and chat_input:
    # Thinking spinner while Ollama/Gemma parses
    with st.spinner("🧠 miseBot is thinking..."):
        action = parse_user_input(chat_input)
    reply = generate_reply(action)
    st.session_state.chat_log.append({"user": chat_input, "bot": reply, "action": action})

    # Execute action
    intent = action.get("intent")
    list_type = action.get("list_type", "shopping")
    items = action.get("items", [])
    qty = action.get("quantity", "")
    unit = action.get("unit", "")
    recipient = action.get("recipient", "")
    time_ref = action.get("time_ref", "")

    if intent == "add" and items:
        lt = list_type if list_type in ("shopping", "prep") else "shopping"
        lst = get_or_create_list(lt)
        added = []
        skipped = []
        for itm in items:
            if not _is_valid_item(itm):
                skipped.append(itm)
                continue
            existing = get_items(lst["id"])
            # Duplicate check
            dup = [e for e in existing if itm.lower() in e["name"].lower() or e["name"].lower() in itm.lower()]
            if dup:
                st.toast(f"⚠️ '{itm}' is already on your {lt} list.")
                continue
            add_item(lst["id"], itm, qty, unit)
            added.append(itm)
        if added:
            st.toast(f"✅ Added {', '.join(added)} to {lt} list")
        if skipped:
            st.toast(f"🤔 Couldn't understand: {', '.join(skipped)}. Try 'Add tomatoes to shopping'")
        if not added and not skipped:
            st.toast("🤔 Couldn't parse items. Try: 'Add tomatoes and onions to shopping'")
        st.session_state.active_tab = lt

    elif intent == "done" and items:
        lt = list_type if list_type in ("shopping", "prep") else "prep"
        lst = get_or_create_list(lt)
        existing = get_items(lst["id"])
        for itm in items:
            match = [e for e in existing if itm.lower() in e["name"].lower() or e["name"].lower() in itm.lower()]
            if match:
                mark_done(match[0]["id"])
        st.session_state.active_tab = lt

    elif intent == "remove" and items:
        lt = list_type if list_type in ("shopping", "prep") else "shopping"
        lst = get_or_create_list(lt)
        existing = get_items(lst["id"])
        for itm in items:
            match = [e for e in existing if itm.lower() in e["name"].lower() or e["name"].lower() in itm.lower()]
            if match:
                remove_item(match[0]["id"])
        st.session_state.active_tab = lt

    elif intent == "email":
        lt = list_type if list_type in ("shopping", "prep") else st.session_state.active_tab
        lst = get_or_create_list(lt)
        items_list = get_items(lst["id"])
        to = recipient or settings.get("email_to", "")
        fr = settings.get("email_from", "")
        if lt == "shopping":
            html = build_shopping_email(items_list, to, fr)
        else:
            html = build_prep_email(items_list, to, fr)
        if to and fr:
            sent = send_email(to, fr, f"miseBot {lt.title()} List", html, settings)
            if sent:
                st.success(f"📧 {lt.title()} list emailed to {to}!")
            else:
                st.error("Email failed. Check settings.")
        else:
            st.warning("Set email addresses in Settings first.")

    elif intent == "schedule":
        # Handle day schedule and reminders
        if time_ref:
            if "noon" in time_ref or "lunch" in chat_input.lower() or "setup" in chat_input.lower():
                # Build day blocks
                blocks = [
                    {"label": "Prep Block", "start": "9:00 AM", "end": "12:00 PM", "items": []},
                    {"label": "Lunch", "start": "12:00 PM", "end": "12:30 PM", "items": []},
                    {"label": "Dinner Setup", "start": "4:30 PM", "end": "5:00 PM", "items": []},
                ]
                # Add current prep items to first block
                prep_lst = get_or_create_list("prep")
                prep_items = get_items(prep_lst["id"])
                if prep_items:
                    blocks[0]["items"] = [i["name"] for i in prep_items]
                for b in blocks:
                    add_time_block(b["label"], b["start"], b["end"], b["items"])
                st.session_state.demo_day_set = True
                st.success("Day schedule set! Prep till noon, lunch, dinner setup at 5.")
            else:
                # Single reminder
                for itm in items:
                    add_reminder(itm, time_ref.strip())
                st.success(f"Reminder set: {', '.join(items)} at {time_ref}")

    st.rerun()

# ─── Chat Log ──────────────────────────────────────────────────────────────────
if st.session_state.chat_log:
    with st.container():
        for msg in st.session_state.chat_log[-3:]:
            st.markdown(f"""
            <div style="background:#f0f0f0; padding:8px; border-radius:8px; margin:4px 0; font-size:13px;">
                <b>You:</b> {msg['user']}<br>
                <b>miseBot:</b> {msg['bot']}
            </div>
            """, unsafe_allow_html=True)

# ─── Demo Seeding ──────────────────────────────────────────────────────────────
if not st.session_state.demo_menu_set:
    with st.expander("🍽️ Set Tonight's Menu (Smart Prep)", expanded=False):
        menu_items = get_menu_items()
        selected = st.multiselect("Select menu items for today:", [m["name"] for m in menu_items], key="menu_select")
        if st.button("Auto-Generate Prep List"):
            prep_lst = get_or_create_list("prep")
            for menu_name in selected:
                menu = [m for m in menu_items if m["name"] == menu_name]
                if menu:
                    for prep_item in menu[0].get("prep_items", []):
                        add_item(prep_lst["id"], prep_item, "1 batch", "batch")
            st.session_state.demo_menu_set = True
            st.success(f"Prep list auto-generated for {len(selected)} menu items!")
            st.rerun()

# ─── Day Keeper Timeline ─────────────────────────────────────────────────────
if st.session_state.demo_day_set:
    st.markdown("<div style='margin:12px 0 4px;'><b>⏱️ Day Keeper</b></div>", unsafe_allow_html=True)
    blocks = get_time_blocks()
    now = datetime.now()
    current_min = now.hour * 60 + now.minute

    for block in blocks:
        start_str = block.get("planned_start", "")
        label = block.get("label", "")
        items = block.get("items", [])

        # Determine status color
        from utils.helpers import time_str_to_minutes
        start_min = time_str_to_minutes(start_str) or 0
        if current_min > start_min + 30:
            css_class = "timeline-block warning"
        elif current_min >= start_min:
            css_class = "timeline-block"
        else:
            css_class = "timeline-block done-block"

        items_html = ""
        if items:
            items_html = "<br><small>" + "<br>".join(f"• {i}" for i in items) + "</small>"

        st.markdown(
            f"""
            <div class="{css_class}">
                <b>{start_str}</b> — {label}{items_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

# ─── Reminders ─────────────────────────────────────────────────────────────────
reminders = get_reminders("pending")
if reminders:
    st.markdown("<div style='margin:8px 0;'><b>⏰ Upcoming</b></div>", unsafe_allow_html=True)
    for r in reminders:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"• **{r['label']}** at {r['trigger_time']}")
        with col2:
            if st.button("✓", key=f"rem_{r['id']}"):
                dismiss_reminder(r["id"])
                st.rerun()

# ─── Tab Toggle ────────────────────────────────────────────────────────────────
tab_cols = st.columns(2)
with tab_cols[0]:
    if st.button("🍳 Prep List", key="tab_prep", use_container_width=True):
        st.session_state.active_tab = "prep"
        st.rerun()
with tab_cols[1]:
    if st.button("🛒 Shopping List", key="tab_shopping", use_container_width=True):
        st.session_state.active_tab = "shopping"
        st.rerun()

# Highlight active tab
if st.session_state.active_tab == "prep":
    st.markdown("""
    <style>#tab_prep button { background: #C41E3A !important; color: white !important; }</style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>#tab_shopping button { background: #C41E3A !important; color: white !important; }</style>
    """, unsafe_allow_html=True)

# ─── Prep List ────────────────────────────────────────────────────────────────
prep_lst = get_or_create_list("prep")
prep_items = get_items(prep_lst["id"])

if st.session_state.active_tab == "prep":
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin:8px 0;">
        <b>🍳 Prep List</b>
        <span style="color:#888; font-size:12px;">{len([i for i in prep_items if i['status']=='done'])}/{len(prep_items)} done</span>
    </div>
    """, unsafe_allow_html=True)

    # Progress bar
    if prep_items:
        done_count = len([i for i in prep_items if i["status"] == "done"])
        pct = int((done_count / len(prep_items)) * 100)
        st.progress(pct / 100)

        # Confetti on 100%
        if pct == 100 and not st.session_state.confetti_fired:
            st.balloons()
            st.session_state.confetti_fired = True
            st.markdown("""
            <script>
            for(let i=0; i<30; i++) {
                let c = document.createElement('div');
                c.className = 'confetti-piece';
                c.style.left = Math.random()*100 + 'vw';
                c.style.background = ['#C41E3A','#2E7D32','#F57C00','#1A1A1A'][Math.floor(Math.random()*4)];
                c.style.animationDuration = (2+Math.random()*2) + 's';
                document.body.appendChild(c);
                setTimeout(()=> c.remove(), 4000);
            }
            </script>
            """, unsafe_allow_html=True)
        elif pct < 100:
            st.session_state.confetti_fired = False

    # Add item form
    with st.form("add_prep", clear_on_submit=True):
        cols = st.columns([3, 1, 1])
        with cols[0]:
            new_prep = st.text_input("Add prep item...", key="new_prep_name", label_visibility="collapsed")
        with cols[1]:
            new_prep_qty = st.text_input("Qty", placeholder="1", key="new_prep_qty", label_visibility="collapsed")
        with cols[2]:
            st.form_submit_button("➕")

    if new_prep:
        add_item(prep_lst["id"], new_prep, new_prep_qty or "1", "batch")
        st.toast(f"Added '{new_prep}' to prep list")
        st.rerun()

    # List items
    for item in prep_items:
        cols = st.columns([5, 2, 1, 1])
        with cols[0]:
            name_class = "done-item" if item["status"] == "done" else ""
            st.markdown(
                f"""
                <div class="list-item-row slide-in">
                    <div class="item-info">
                        <div class="item-name {name_class}">{item['name']}</div>
                        <div class="item-meta">{item.get('quantity','')} {item.get('unit','')}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with cols[1]:
            if item["status"] == "pending":
                if st.button("✓ Done", key=f"done_p_{item['id']}"):
                    mark_done(item["id"])
                    st.rerun()
            else:
                if st.button("↩ Undo", key=f"undo_p_{item['id']}"):
                    mark_pending(item["id"])
                    st.rerun()
        with cols[2]:
            if st.button("🗑️", key=f"del_p_{item['id']}"):
                remove_item(item["id"])
                st.rerun()

    # Email button
    if prep_items:
        if st.button("📧 Email Prep List", use_container_width=True, key="email_prep"):
            to = settings.get("email_to", "")
            fr = settings.get("email_from", "")
            if to and fr:
                html = build_prep_email(prep_items, to, fr)
                sent = send_email(to, fr, "miseBot Prep List", html, settings)
                if sent:
                    st.success(f"Sent to {to}!")
                else:
                    st.error("Failed. Check settings.")
            else:
                st.warning("Configure email in Settings first.")

# ─── Shopping List ─────────────────────────────────────────────────────────────
shop_lst = get_or_create_list("shopping")
shop_items = get_items(shop_lst["id"])

if st.session_state.active_tab == "shopping":
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin:8px 0;">
        <b>🛒 Shopping List</b>
        <span style="color:#888; font-size:12px;">{len(shop_items)} items</span>
    </div>
    """, unsafe_allow_html=True)

    # Add item form
    with st.form("add_shop", clear_on_submit=True):
        cols = st.columns([3, 1, 1])
        with cols[0]:
            new_shop = st.text_input("Add item...", key="new_shop_name", label_visibility="collapsed")
        with cols[1]:
            new_shop_qty = st.text_input("Qty", placeholder="1", key="new_shop_qty", label_visibility="collapsed")
        with cols[2]:
            st.form_submit_button("➕")

    if new_shop:
        add_item(shop_lst["id"], new_shop, new_shop_qty or "1", "ea")
        st.toast(f"Added '{new_shop}' to shopping list")
        st.rerun()

    # List items
    for item in shop_items:
        cols = st.columns([5, 2, 1, 1])
        with cols[0]:
            name_class = "done-item" if item["status"] == "done" else ""
            st.markdown(
                f"""
                <div class="list-item-row slide-in">
                    <div class="item-info">
                        <div class="item-name {name_class}">{item['name']}</div>
                        <div class="item-meta">{item.get('quantity','')} {item.get('unit','')}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with cols[1]:
            if item["status"] == "pending":
                if st.button("✓ Got it", key=f"done_s_{item['id']}"):
                    mark_done(item["id"])
                    st.rerun()
            else:
                if st.button("↩ Need more", key=f"undo_s_{item['id']}"):
                    mark_pending(item["id"])
                    st.rerun()
        with cols[2]:
            if st.button("🗑️", key=f"del_s_{item['id']}"):
                remove_item(item["id"])
                st.rerun()

    # Email button
    if shop_items:
        if st.button("📧 Email Shopping List", use_container_width=True, key="email_shop"):
            to = settings.get("email_to", "")
            fr = settings.get("email_from", "")
            if to and fr:
                html = build_shopping_email(shop_items, to, fr)
                sent = send_email(to, fr, "miseBot Shopping List", html, settings)
                if sent:
                    st.success(f"Sent to {to}!")
                else:
                    st.error("Failed. Check settings.")
            else:
                st.warning("Configure email in Settings first.")

# ─── Settings (Collapsible, bottom of page) ──────────────────────────────────
settings = get_settings()
with st.expander("⚙️ Settings", expanded=False):
    st.subheader("Email Setup")
    email_to = st.text_input("Send lists to", value=settings.get("email_to", ""), key="set_to")
    email_from = st.text_input("From email", value=settings.get("email_from", ""), key="set_from")
    smtp_host = st.text_input("SMTP Host", value=settings.get("smtp_host", "smtp.gmail.com"), key="set_host")
    smtp_port = st.number_input("SMTP Port", value=settings.get("smtp_port", 587), key="set_port")
    smtp_user = st.text_input("SMTP User", value=settings.get("smtp_user", ""), key="set_user")
    smtp_pass = st.text_input("SMTP Password", type="password", value=settings.get("smtp_pass", ""), key="set_pass")

    st.subheader("List Preferences")
    ttl = st.slider("List TTL (days)", 1, 30, settings.get("list_ttl_days", 7), key="set_ttl")
    active_user = st.text_input("Active User", value=settings.get("active_user", "Brianne"), key="set_user_name")

    st.subheader("🛡️ Autonomy Safety")
    auto_enabled = st.toggle("Enable auto-actions", value=settings.get("auto_enabled", True), key="set_auto")
    max_actions = st.slider("Max auto-actions per shift", 5, 50, settings.get("max_auto_actions", 20), key="set_max_auto")
    max_restarts = st.slider("Max restarts per feature/day", 1, 10, settings.get("max_restarts", 3), key="set_max_restart")

    st.subheader("📊 Safety Dashboard")
    counters = get_auto_actions(limit=5)
    safety = get_settings()
    st.markdown(f"""
    <div style="font-size:12px; color:#555;">
    • Auto-actions today: {safety.get('auto_action_count', 0)} / {max_actions}<br>
    • Restarts today: {safety.get('restart_count', 0)} / {max_restarts}<br>
    • Recent actions: {len(counters)}<br>
    • Phase: {get_autonomy_phase('Coffee')}
    </div>
    """, unsafe_allow_html=True)

    if st.button("💾 Save Settings"):
        save_settings(
            email_to=email_to,
            email_from=email_from,
            smtp_host=smtp_host,
            smtp_port=int(smtp_port),
            smtp_user=smtp_user,
            smtp_pass=smtp_pass,
            list_ttl_days=int(ttl),
            active_user=active_user,
            auto_enabled=auto_enabled,
            max_auto_actions=int(max_actions),
            max_restarts=int(max_restarts),
        )
        st.success("Settings saved!")
        st.rerun()

    st.markdown("---")
    st.subheader("🧨 Demo Reset")
    if st.button("Clear all lists, schedule, and reminders"):
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM list_items")
        cursor.execute("DELETE FROM lists WHERE status = 'active'")
        cursor.execute("DELETE FROM time_blocks")
        cursor.execute("DELETE FROM reminders")
        conn.commit()
        conn.close()
        st.session_state.demo_menu_set = False
        st.session_state.demo_day_set = False
        st.session_state.chat_log = []
        st.session_state.last_chat_input = ""
        st.success("Demo data cleared!")
        st.rerun()

# ─── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; color:#888; font-size:11px; margin-top:12px;">
    miseBot v0.1 — Your AI Sous-Chef
</div>
""", unsafe_allow_html=True)
