import streamlit as st
import pandas as pd
import requests
import json
import random

# --- 1. CẤU HÌNH HỆ THỐNG & GIAO DIỆN (CSS) ---
st.set_page_config(page_title="Nga Ngữ Expert v25", layout="centered", page_icon="🇷🇺")

# CSS Custom: Làm đẹp hộp câu hỏi, bảng biến cách và tô đậm đuôi từ
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    .stApp h1 { color: #1e3a8a; text-align: center; border-bottom: 3px solid #e63946; padding-bottom: 10px; }
    .ques-box {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 15px;
        border-left: 10px solid #e63946;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        margin: 25px 0;
    }
    .ques-vn { color: #1e293b; font-size: 30px !important; font-weight: 800; text-align: center; }
    table { width: 100%; border-collapse: collapse; margin-top: 15px; background-color: white; }
    th { background-color: #f1f5f9; color: #1e3a8a; font-weight: bold; text-align: center !important; padding: 12px; }
    td { border: 1px solid #cbd5e1; padding: 12px; text-align: left; }
    b, strong { color: #e63946; font-weight: bold; } /* Tô đậm đuôi biến cách màu đỏ */
</style>
""", unsafe_allow_html=True)

# Lấy API Key từ Secrets
api_key = st.secrets.get("GROQ_API_KEY")

def call_groq_v25(word_ru, word_vn):
    if not api_key: return "⚠️ Lỗi: Chưa cấu hình GROQ_API_KEY trong Secrets."
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # PROMPT TỐI ƯU: NGA HÓA 100%, CHỈ KHẲNG ĐỊNH ĐÚNG, TÔ ĐẬM ĐUÔI
    prompt = f"""
    Phân tích từ tiếng Nga: '{word_ru}' ({word_vn}).
    
    YÊU CẦU TR
