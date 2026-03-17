import streamlit as st
import pandas as pd
import requests
import json
import random

# --- CẤU HÌNH ---
st.set_page_config(page_title="Học Tiếng Nga AI", layout="centered")

# Lấy API KEY từ Secrets
api_key = st.secrets.get("GEMINI_API_KEY")

def call_gemini_direct(prompt):
    """Gọi trực tiếp vào Google API bằng HTTP để tránh lỗi thư viện cũ"""
    if not api_key:
        return "Lỗi: Chưa cấu hình API Key trong Secrets."
    
    # Địa chỉ gọi thẳng vào Google
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            res_json = response.json()
            return res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Lỗi máy chủ Google ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Lỗi kết nối: {str(e)}"

# --- QUẢN LÝ TRẠNG THÁI ---
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'data' not in st.session_state: st.session_state.data = None

st.title("🇷🇺 Russian Master AI")

# --- NẠP DỮ LIỆU ---
with st.sidebar:
    st.header("Dữ liệu từ vựng")
    uploaded_file = st.file_uploader("Nạp file Excel (.xlsx)", type=["xlsx"])
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            df.columns = [str(c).strip().lower() for c in df.columns]
            st.session_state.data = df
            st.success("Đã nạp file thành công!")
        except Exception as e:
            st.error(f"Lỗi đọc file: {e}")

# --- GIAO DIỆN HÀNH ĐỘNG ---
if st.session_state.data is not None:
    df = st.session_state.data
    col_ru = next((c for c in df.columns if any(k in c for k in ['nga', 'ru'])), None)
    col_vn = next((c for c in df.columns if any(k in c for k in ['việt', 'vn', 'viet'])), None)

    if col_ru and col_vn:
        row = df.iloc[st.session_state.idx]
        word_vn = str(row[col_vn]).strip()
        word_ru = str(row[col_ru]).strip()

        st.markdown(f"### Dịch sang tiếng Nga: <span style='color:red'>{word_vn}</span>", unsafe_allow_html=True)
        user_input = st.text_input("Gõ đáp án của bạn:", key=f"in_{st.session_state.idx}")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Kiểm tra & Giải thích AI"):
                if user_input.strip().lower() == word_ru.lower():
                    st.success(f"Chính xác! Đáp án: {word_ru}")
                else:
                    st.error(f"Chưa đúng. Đáp án: {word_ru}")
                
                with st.spinner("AI đang soạn bài phân tích..."):
                    prompt = f"Phân tích từ tiếng Nga '{word_ru}' (nghĩa: {word_vn}). Giải thích ngữ pháp ngắn gọn và đặt 1 ví dụ quân sự/kỹ thuật Nga-Việt."
                    analysis = call_gemini_direct(prompt)
                    st.info(analysis)
        
        with c2:
            if st.button("Từ tiếp theo ➡️"):
                st.session_state.idx = random.randint(0, len(df)-1)
                st.rerun()
    else:
        st.error("File Excel cần có cột 'Tiếng Nga' và 'Tiếng Việt'.")
else:
    st.info("Hãy tải file Excel lên từ cột bên trái.")
