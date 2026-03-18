import streamlit as st
import pandas as pd
import requests
import random

# 1. CẤU HÌNH GIAO DIỆN & STYLE (LÀM ĐẸP)
st.set_page_config(page_title="Nga Ngữ Expert v27.1", layout="centered", page_icon="🇷🇺")

st.markdown("""
<style>
    /* Làm đẹp tiêu đề chính */
    .stApp h1 { color: #1e3a8a; text-align: center; border-bottom: 3px solid #e63946; padding-bottom: 10px; }
    
    /* Hộp câu hỏi Tiếng Việt nổi bật */
    .ques-vn { 
        font-size: 32px !important; 
        font-weight: 800; 
        color: #1e293b; 
        text-align: center; 
        padding: 25px; 
        background-color: #ffffff; 
        border-radius: 15px; 
        border-left: 10px solid #e63946; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 25px; 
    }
    
    /* Style cho phần tô đậm đuôi từ trong bảng */
    b, strong { color: #dc2626; font-weight: bold; } 
    
    /* Làm đẹp bảng hiển thị */
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th { background-color: #f1f5f9; padding: 10px; border: 1px solid #cbd5e1; color: #1e3a8a; font-weight: bold; }
    td { border: 1px solid #cbd5e1; padding: 10px; text-align: left; }
    
    /* Style cho Sidebar */
    .css-163914f { background-color: #f8fafc; }
</style>
""", unsafe_allow_html=True)

# 2. HÀM GỌI AI THÔNG MINH (TỰ NHẬN DIỆN VERB/NOUN)
def call_ai_smart(word_ru, word_vn):
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api
