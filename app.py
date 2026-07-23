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
)
from data.seed_data import run_seed
from bot_engine import parse_user_input, generate_reply
from email_sender import build_shopping_email, build_prep_email, send_email
from components.mobile_frame import inject_mobile_css
from components.logo_b64 import LOGO_B64
from utils.helpers import check_low_stock

# ─── Init ────────────────────────────────────────────────────────────────────
init_db()
if "seeded" not in st.session_state:
    run_seed()
    st.session_state.seeded = True

st.set_page_config(page_title="miseBot", page_icon="🍳", layout="centered")
inject_mobile_css()

# ─── Session State ───────────────────────────────────────────────────────────
defaults = {
    "chat_log": [],
    "active_tab": "prep",
    "prep_collapsed": False,
    "shopping_collapsed": False,
    "settings_open": False,
    "demo_menu_set": False,
    "demo_day_set": False,
    "confetti_fired": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── Settings ────────────────────────────────────────────────────────────────
settings = get_settings()

# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="app-header">
        <div class="app-logo">
            <img src="data:image/png;base64,{LOGO_B64}" alt="miseBot" style="width:36px; height:36px; border-radius:6px;">
            <span class="app-title">miseBot</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Gear icon
if st.button("⚙️", key="gear_btn", help="Settings"):
    st.session_state.settings_open = not st.session_state.settings_open

# ─── Settings Modal ──────────────────────────────────────────────────────────
if st.session_state.settings_open:
    with st.expander("⚙️ Settings", expanded=True):
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
            )
            st.success("Settings saved!")
            st.session_state.settings_open = False
            st.rerun()

# ─── Chat Input ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin: 8px 0;">
    <small style="color:#555555;">Tell me your day... Try: "Add tomatoes to shopping" or "I finished whipped feta"</small>
</div>
""", unsafe_allow_html=True)

chat_input = st.text_input("", placeholder="Type a command...", key="chat_input", label_visibility="collapsed")

if chat_input:
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
        for itm in items:
            existing = get_items(lst["id"])
            # Duplicate check
            dup = [e for e in existing if itm.lower() in e["name"].lower() or e["name"].lower() in itm.lower()]
            if dup:
                st.toast(f"⚠️ '{itm}' is already on your {lt} list. Add more or keep as-is.")
            add_item(lst["id"], itm, qty, unit)
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

# ─── Smart Suggestions ─────────────────────────────────────────────────────────
ingredients = get_ingredients()
low_stock_alerts = []
for ing in ingredients:
    if ing.get("current_stock") is not None and ing.get("min_stock") is not None and ing.get("usage_rate_per_week"):
        days = check_low_stock(ing["current_stock"], ing["min_stock"], ing["usage_rate_per_week"])
        if days is not None and days <= 3:
            low_stock_alerts.append(
                f"{ing['name']} — {days} days left (stock: {ing['current_stock']})"
            )

if low_stock_alerts:
    st.markdown("<div style='margin:8px 0;'><b>🔔 Smart Suggestions</b></div>", unsafe_allow_html=True)
    for alert in low_stock_alerts[:3]:
        if st.button(f"➕ {alert}", key=f"alert_{alert[:20]}"):
            lst = get_or_create_list("shopping")
            name = alert.split(" — ")[0]
            add_item(lst["id"], name, "1", "ea")
            st.toast(f"Added {name} to shopping list")
            st.rerun()

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

# ─── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; color:#888; font-size:11px; margin-top:12px;">
    miseBot v0.1 — Your AI Sous-Chef
</div>
""", unsafe_allow_html=True)
