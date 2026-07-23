"""CSS mobile-first styling for Streamlit — no fake phone frame."""
import streamlit as st

MOBILE_CSS = """
<style>
    /* Mobile-first narrow container */
    .main .block-container {
        max-width: 375px !important;
        padding-left: 8px !important;
        padding-right: 8px !important;
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
    }

    /* Force all text darker — override Streamlit greys */
    body, p, span, div, label, .stMarkdown, .stTextInput, .stButton > button,
    .stSelectbox, .stMultiselect, .stCheckbox, .stRadio, .stSlider {
        color: #1A1A1A !important;
    }

    /* Specifically target Streamlit's grey helper text */
    .stCaption, .stTooltipIcon, .stInfo, .stWarning, .stSuccess,
    [data-testid="stMarkdownContainer"] > div > p {
        color: #1A1A1A !important;
    }

    /* Placeholder text darker */
    ::placeholder {
        color: #555555 !important;
        opacity: 1 !important;
    }

    /* Confetti keyframes */
    @keyframes confetti-fall {
        0% { transform: translateY(-100%) rotate(0deg); opacity: 1; }
        100% { transform: translateY(100vh) rotate(720deg); opacity: 0; }
    }
    .confetti-piece {
        position: fixed;
        width: 10px;
        height: 10px;
        top: -10px;
        z-index: 99999;
        animation: confetti-fall 3s ease-out forwards;
    }

    /* Slide-in animation for list items */
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    .slide-in {
        animation: slideIn 0.3s ease-out;
    }

    /* Strikethrough animation */
    .done-item {
        text-decoration: line-through;
        color: #2E7D32 !important;
        opacity: 0.7;
        transition: all 0.3s ease;
    }

    /* Timeline styles */
    .timeline-block {
        border-left: 3px solid #C41E3A;
        padding-left: 12px;
        margin-bottom: 10px;
        position: relative;
    }
    .timeline-block::before {
        content: '';
        width: 10px;
        height: 10px;
        background: #C41E3A;
        border-radius: 50%;
        position: absolute;
        left: -6.5px;
        top: 2px;
    }
    .timeline-block.warning {
        border-left-color: #F57C00;
    }
    .timeline-block.warning::before {
        background: #F57C00;
    }
    .timeline-block.done-block {
        border-left-color: #2E7D32;
    }
    .timeline-block.done-block::before {
        background: #2E7D32;
    }

    /* Custom button styles */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
    }

    /* Smart suggestion chips */
    .suggestion-chip {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 16px;
        background: #FFF3E0;
        color: #E65100;
        font-size: 12px;
        font-weight: 600;
        margin: 2px;
        border: 1px solid #FFE0B2;
    }

    /* Header */
    .app-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
    }
    .app-logo {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .app-title {
        font-size: 18px;
        font-weight: 700;
        color: #1A1A1A;
        margin: 0;
    }

    /* Progress bar */
    .progress-bar-container {
        width: 100%;
        height: 6px;
        background: #E0E0E0;
        border-radius: 3px;
        overflow: hidden;
        margin: 8px 0;
    }
    .progress-bar-fill {
        height: 100%;
        background: #2E7D32;
        border-radius: 3px;
        transition: width 0.5s ease;
    }

    /* List item row */
    .list-item-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 4px;
        border-bottom: 1px solid #f0f0f0;
    }
    .list-item-row:hover {
        background: #f9f9f9;
    }
    .item-info {
        flex: 1;
    }
    .item-name {
        font-weight: 600;
        font-size: 14px;
        color: #1A1A1A !important;
    }
    .item-meta {
        font-size: 11px;
        color: #555555 !important;
    }

    /* Email preview table */
    .email-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
    }
    .email-table th, .email-table td {
        border: 1px solid #ddd;
        padding: 6px 8px;
        text-align: left;
    }
    .email-table th {
        background: #f5f5f5;
        font-weight: 700;
    }
    .email-table .checkbox-col {
        width: 30px;
        text-align: center;
    }

    /* Make Streamlit expander text dark too */
    .streamlit-expanderHeader {
        color: #1A1A1A !important;
    }
    .streamlit-expanderContent {
        color: #1A1A1A !important;
    }

    /* Toast text */
    .toast {
        color: #1A1A1A !important;
    }
</style>
"""


def inject_mobile_css():
    st.markdown(MOBILE_CSS, unsafe_allow_html=True)
