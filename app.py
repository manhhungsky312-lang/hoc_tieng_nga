import streamlit as st
import pandas as pd
import requests
import random

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Nga Ngữ Expert v40", layout="centered", page_icon="🇷🇺")

st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    .stApp h1 { color: #1e3a8a; text-align: center; border-bottom: 3px solid #e63946; }
    .ques-box {
        background-color: #ffffff; padding: 25px; border-radius: 15px;
        border-left: 10px solid #e63946; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 20px 0;
    }
    .ques-vn { color: #1e293b; font-size: 32px !important; font-weight: 800; text-align: center; }
    b, strong { color: #dc2626; font-weight: bold; } 
    table { width: 100%; border-collapse: collapse; margin-top: 15px; background: white; }
    th { background-color: #f1f5f9; padding: 10px; border: 1px solid #cbd5e1; color: #1e3a8a; }
    td { border: 1px solid #cbd5e1; padding: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 2. HÀM GỌI AI (FIX GIỐNG & ĐẶT CÂU TỰ NHIÊN) ---
def call_ai_pro(word_ru, word_vn):
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key: return "⚠️ Thiếu API Key trong Secrets."
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    prompt = f"""
    Phân tích từ: '{word_ru}' ({word_vn}).
    - XÁC ĐỊNH GIỐNG (GENDER): Kiểm tra kỹ đuôi. Ví dụ 'Песня' (-я) là Giống cái (Женский род).
    - DANH TỪ: Chia 6 cách số ít & số nhiều (Danh, Sinh, Tặng, Đối, Công cụ, Giới từ). Chuyển sang tính từ.
    - ĐỘNG TỪ: Chia 6 ngôi hiện tại; Quá khứ (4 dạng); Mệnh lệnh thức (ты, вы).
    - TÍNH TỪ: Chia 6 cách; Tính từ ngắn đuôi (Краткая форма).
    - ĐẶT CÂU: Cung cấp 3 ví dụ đặt câu tự nhiên nhất (Nga - Việt).
    Lưu ý: Tô đậm đuôi biến đổi bằng **.
    """
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Giáo viên tiếng Nga bản ngữ. Xác định giống chính xác 100%. Đặt câu tự nhiên, không máy móc quân sự."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        return r.json()['choices'][0]['message']['content']
    except: return "⚠️ AI đang bận."

# --- 3. KHỞI TẠO SESSION STATE ---
if 'pool' not in st.session
