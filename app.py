import streamlit as st
import pandas as pd
import requests
import json
import random

# --- 1. CẤU HÌNH & GIAO DIỆN (CSS) ---
st.set_page_config(page_title="Nga Ngữ Chuyên Sâu v24", layout="centered", page_icon="🇷🇺")

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
    /* Style cho bảng biến cách */
    table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    th { background-color: #f1f5f9; color: #1e3a8a; font-weight: bold; text-align: center !important; }
    td { border: 1px solid #cbd5e1; padding: 10px; text-align: left; }
    b { color: #e63946; } /* Tô màu đỏ cho phần đuôi được tô đậm */
</style>
""", unsafe_allow_html=True)

api_key = st.secrets.get("GROQ_API_KEY")

def call_groq_v24(word_ru, word_vn):
    if not api_key: return "⚠️ Thiếu API Key."
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # PROMPT ÉP AI CHUẨN HÓA NGỮ PHÁP & TÔ ĐẬM ĐUÔI
    prompt = f"""
    Phân tích từ tiếng Nga: '{word_ru}' ({word_vn}).
    
    YÊU CẦU NGHIÊM NGẶT:
    1. XÁC ĐỊNH GIỐNG (Род): Kiểm tra kỹ đuôi từ. 
       - Đuôi -а/-я là Женский род (Giống cái). KHÔNG nhầm sang Trung tính.
       - Chỉ khẳng định giống đúng, KHÔNG liệt kê những gì không phải.
    2. BẢNG BIẾN CÁCH (Склонение): Lập bảng so sánh Ед. ч. và Мн. ч.
       - Tên các cách dùng TIẾNG NGA 100%: Именительный, Родительный, Дательный, Винительный, Творительный, Предложный.
       - TÔ ĐẬM phần đuôi biến đổi bằng cách dùng thẻ <b>...</b> hoặc **...**.
    3. ĐỘNG TỪ (Глагол): Gợi ý 1 động từ hay đi kèm, chia 6 ngôi hiện tại (Я, Ты, Он/Она, Мы, Вы, Они).
       - Chú ý đuôi động từ nhóm 2 (như смотреть -> смотришь).
    4. VÍ DỤ: 
       - Câu 1: Tính từ + Số ít.
       - Câu 2: Giới từ + Số nhiều.
       - Câu 3: Giao tiếp tự nhiên.
    (Ví dụ có tiếng Nga và dịch Việt).
    """
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Bạn là chuyên gia ngôn ngữ Nga khắt khe. Trình bày khoa học, tập trung vào bảng biến cách chuẩn xác và tô đậm đuôi từ."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        return response.json()['choices'][0]['message']['content']
    except: return "⚠️ AI bận. Hãy tiếp tục."

# --- 2. QUẢN LÝ TRẠNG THÁI ---
if 'pool' not in st.session_state: st.session_state.pool =
