# Autor: Michał Wlazło (s160760)
import streamlit as st

def apply_custom_styles():
    # dodanie ciemnego motywu css stylizowanego na sklep steam
    st.markdown("""
        <style>
        .stApp {
            background-color: #101822;
            color: #c7d5e0;
            font-family: 'Inter', 'Segoe UI', sans-serif;
        }

        h1, h2, h3 {
            color: #ffffff !important;
            font-weight: 700 !important;
        }
        
        h1 span {
            color: #66c0f4;
        }

        section[data-testid="stSidebar"] {
            background-color: #1b2838;
            border-right: 1px solid #2a475e;
        }
        
        section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
            color: #66c0f4 !important;
        }

        div[data-testid="stMetric"] {
            background-color: #1e3044;
            border: 1px solid #2a475e;
            padding: 15px;
            border-radius: 8px;
        }
        
        div[data-testid="stMetric"] label {
            color: #8f98a0 !important;
            font-size: 0.9rem !important;
        }
        
        div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
            color: #66c0f4 !important;
            font-size: 2rem !important;
            font-weight: bold !important;
        }

        div[data-testid="stTabs"] button[role="tab"] {
            color: #8f98a0;
            font-size: 1rem;
            padding: 10px 20px;
        }
        
        div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
            color: #ffffff !important;
            background-color: #2a475e !important;
            border-bottom: 3px solid #66c0f4 !important;
        }

        .business-comment {
            background-color: rgba(42, 71, 94, 0.3);
            border-left: 4px solid #66c0f4;
            padding: 12px 15px;
            border-radius: 4px;
            margin-top: 10px;
            margin-bottom: 20px;
            font-size: 0.95rem;
            color: #dcdedf;
        }
        
        .business-comment strong {
            color: #66c0f4;
        }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

def render_business_comment(title, comment_text):
    # wyswietla prosty blok z opisem wniosku pod wykresem
    st.markdown(f"""
        <div class="business-comment">
            <strong>Wniosek z wykresu ({title}):</strong><br>
            {comment_text}
        </div>
    """, unsafe_allow_html=True)
