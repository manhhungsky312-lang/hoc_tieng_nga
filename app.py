import streamlit as st
import pandas as pd
import requests
import random

# 1. CẤU HÌNH CƠ BẢN (BỎ HẾT LINH TINH)
st.set_page_config(page_title="Học Tiếng Nga v26", layout="centered")

# CSS tối giản cho bảng và phần tô đậm
st.markdown("""
<style>
    .ques-vn { font-size: 32px !important; font-weight: bold; color: #1e293b; text-align: center; padding: 20px; border: 2px solid #e2e8f0; border-radius: 10px; margin-bottom: 20px; }
    b, strong { color: #dc2626; } /* Tô đậm đuôi biến đổi màu đỏ */
    table { width: 100%; border-collapse: collapse; }
    th, td { border: 1px solid #cbd5e1; padding: 8px; text-align: left; }
</style>
""", unsafe_allow_html=True)

# 2. HÀM GỌI AI (CHỈ LẤY KIẾN THỨC CHUẨN)
def call_ai_russian(word_ru, word_vn):
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key: return "Lỗi: Thiếu API Key trong Secrets."
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    prompt = f"""
    Phân tích từ: '{word_ru}' ({word_vn}).
    Yêu cầu:
    1. Giống (Род) & Loại biến cách. (Chỉ khẳng định đúng, không nói rườm rà).
    2. Bảng biến cách 6 cách (Tên cách bằng TIẾNG NGA: Именительный, Родительный, Дательный, Винительный, Творительный, Предложный). 
    3. Chia Số ít (Ед. ч.) và Số nhiều (Мн. ч.). Tô đậm đuôi bằng dấu **.
    4. 3 ví dụ (Tính từ, Giới từ, Giao tiếp).
    """
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1
    }
    
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        return r.json()['choices'][0]['message']['content']
    except: return "AI đang bận, hãy thử lại."

# 3. QUẢN LÝ DỮ LIỆU
if 'pool' not in st.session_state: st.session_state.pool = []
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'ans' not in st.session_state: st.session_state.ans = ""

# 4. GIAO DIỆN NẠP FILE (SIDEBAR)
with st.sidebar:
    f = st.file_uploader("Nạp file Excel", type=["xlsx"])
    if f and st.button("BẮT ĐẦU HỌC"):
        df = pd.read_excel(f)
        df.columns = [str(c).strip().lower() for c in df.columns]
        st.session_state.pool = df.to_dict('records')
        st.session_state.idx = 0
        st.session_state.ans = ""
        st.rerun()

# 5. GIAO DIỆN CHÍNH
st.title("Học Tiếng Nga v26")

if st.session_state.pool:
    item = st.session_state.pool[st.session_state.idx]
    # Tìm cột Nga/Việt
    c_ru = next((k for k in item.keys() if 'nga' in k or 'ru' in k), None)
    c_vn = next((k for k in item.keys() if 'việt' in k or 'vn' in k), None)

    if c_ru and c_vn:
        w_ru = str(item[c_ru]).strip()
        w_vn = str(item[c_vn]).strip()

        st.markdown(f'<div class="ques-vn">{w_vn}</div>', unsafe_allow_html=True)
        
        with st.form(key="study_form"):
            u_input = st.text_input("Đáp án tiếng Nga:", key="input_text")
            btn = st.form_submit_button("KIỂM TRA")

        if btn:
            if u_input.strip().lower() == w_ru.lower():
                st.success(f"ĐÚNG! Đáp án: {w_ru}")
                st.session_state.ans = call_ai_russian(w_ru, w_vn)
            else:
                st.error(f"SAI! Đáp án đúng: {w_ru}")
                # Nhét vào cuối để học lại
                st.session_state.pool.append(item)

        if st.session_state.ans:
            st.markdown(st.session_state.ans)
            if st.button("Từ tiếp theo ➡️"):
                st.session_state.pool.pop(st.session_state.idx)
                if st.session_state.idx >= len(st.session_state.pool): st.session_state.idx = 0
                st.session_state.ans = ""
                st.rerun()
    else:
        st.error("File Excel thiếu cột 'Nga' hoặc 'Việt'.")
else:
    st.info("Hãy nạp file Excel ở thanh bên để bắt đầu.")
