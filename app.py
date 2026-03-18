import streamlit as st
import pandas as pd
import requests
import json
import random

# --- 1. CẤU HÌNH & GIAO DIỆN ---
st.set_page_config(page_title="Nga Ngữ Expert v24.1", layout="centered", page_icon="🇷🇺")

st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    .stApp h1 { color: #1e3a8a; text-align: center; border-bottom: 3px solid #e63946; padding-bottom: 10px; }
    .ques-box {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 15px;
        border-left: 8px solid #e63946;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin: 20px 0;
    }
    .ques-vn { color: #1e293b; font-size: 28px !important; font-weight: 800; }
    table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    th { background-color: #f1f5f9; color: #1e3a8a; font-weight: bold; text-align: center !important; }
    td { border: 1px solid #cbd5e1; padding: 10px; text-align: left; }
    b { color: #e63946; } 
</style>
""", unsafe_allow_html=True)

api_key = st.secrets.get("GROQ_API_KEY")

def call_groq_v24(word_ru, word_vn):
    if not api_key: return "⚠️ Lỗi: Chưa có API Key trong phần Secrets."
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    prompt = f"""
    Phân tích từ tiếng Nga: '{word_ru}' ({word_vn}).
    
    YÊU CẦU:
    1. NGỮ PHÁP (ГРАММАТИКА): Chỉ nêu Giống (Род) và Loại biến cách (Склонение). KHÔNG phủ định rườm rà.
    2. BẢNG BIẾN CÁCH (Склонение): Lập bảng so sánh Ед. ч. và Мн. ч.
       - Tên 6 cách dùng tiếng Nga: Именительный, Родительный, Дательный, Винительный, Творительный, Предложный.
       - TÔ ĐẬM phần đuôi biến đổi bằng dấu ** (ví dụ: Песн**я**).
    3. ĐỘNG TỪ (Глагол): Gợi ý 1 động từ đi kèm, chia 6 ngôi hiện tại.
    4. VÍ DỤ: 3 câu (Tính từ, Giới từ, Giao tiếp). Có dịch Việt.
    """
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Bạn là chuyên gia ngôn ngữ Nga. Trình bày bảng Markdown chuẩn, súc tích, tô đậm đuôi từ."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"⚠️ Lỗi kết nối AI: {str(e)}"

# --- 2. QUẢN LÝ TRẠNG THÁI ---
if 'pool' not in st.session_state: st.session_state.pool = [] 
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'status' not in st.session_state: st.session_state.status = None 
if 'ai_response' not in st.session_state: st.session_state.ai_response = ""

# --- 3. SIDEBAR ---
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1513326738677-b964603b136d?q=80&w=400", caption="🇷🇺 Nước Nga")
    uploaded_file = st.file_uploader("Nạp file Excel vựng", type=["xlsx"])
    if uploaded_file and not st.session_state.pool:
        df = pd.read_excel(uploaded_file)
        df.columns = [str(c).strip().lower() for c in df.columns]
        st.session_state.pool = df.to_dict('records')
        random.shuffle(st.session_state.pool)
        st.rerun() # Làm mới để nạp dữ liệu ngay
    st.image("https://images.unsplash.com/photo-1504457047772-27fad17438e2?q=80&w=400", caption="🇻🇳 Việt Nam")

# --- 4. GIAO DIỆN CHÍNH ---
st.title("🇷🇺 Russian Expert v24.1 🇻🇳")

if st.session_state.pool:
    current_word = st.session_state.pool[st.session_state.idx]
