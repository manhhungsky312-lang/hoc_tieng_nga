import streamlit as st
import pandas as pd
import requests
import random

# --- CẤU HÌNH ---
st.set_page_config(page_title="Học Tiếng Nga AI (Llama 3.3)", layout="centered")

# Lấy API KEY của Groq từ Secrets
api_key = st.secrets.get("GROQ_API_KEY")

def call_ai_analysis(prompt):
    """Gọi AI của Groq (Llama 3.3) - Model mới nhất không bị decommissioned"""
    if not api_key:
        return "Lỗi: Chưa cấu hình GROQ_API_KEY trong Secrets."
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile", # ĐÃ CẬP NHẬT MODEL MỚI NHẤT
        "messages": [
            {"role": "system", "content": "Bạn là chuyên gia tiếng Nga chuyên ngành quân sự và kỹ thuật. Trả lời ngắn gọn, chính xác bằng tiếng Việt."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Lỗi từ Groq: {response.text}"
    except Exception as e:
        return f"Lỗi kết nối: {str(e)}"

# --- PHẦN CÒN LẠI GIỮ NGUYÊN ---
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'data' not in st.session_state: st.session_state.data = None

st.title("🇷🇺 Luyện Tiếng Nga với Llama 3.3")

with st.sidebar:
    st.header("Cài đặt")
    uploaded_file = st.file_uploader("Nạp file Excel (.xlsx)", type=["xlsx"])
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            df.columns = [str(c).strip().lower() for c in df.columns]
            st.session_state.data = df
            st.success("Đã nạp file thành công!")
        except:
            st.error("Lỗi đọc file Excel.")

if st.session_state.data is not None:
    df = st.session_state.data
    col_ru = next((c for c in df.columns if any(k in c for k in ['nga', 'ru'])), None)
    col_vn = next((c for c in df.columns if any(k in c for k in ['việt', 'vn', 'viet'])), None)

    if col_ru and col_vn:
        row = df.iloc[st.session_state.idx]
        word_vn, word_ru = str(row[col_vn]).strip(), str(row[col_ru]).strip()

        st.markdown(f"### Dịch sang tiếng Nga: **{word_vn}**")
        user_input = st.text_input("Gõ đáp án:", key=f"in_{st.session_state.idx}")

        if st.button("Kiểm tra & Giải thích AI"):
            if user_input.strip().lower() == word_ru.lower():
                st.success(f"Chính xác! Đáp án: {word_ru}")
            else:
                st.error(f"Sai rồi. Đáp án đúng: {word_ru}")
            
            with st.spinner("AI đang phân tích..."):
                prompt = f"Phân tích từ tiếng Nga '{word_ru}' (nghĩa: {word_vn}). Giải thích ngữ pháp ngắn gọn và đặt 1 ví dụ quân sự Nga-Việt."
                analysis = call_ai_analysis(prompt)
                st.info(analysis)
        
        if st.button("Từ tiếp theo ➡️"):
            st.session_state.idx = random.randint(0, len(df)-1)
            st.rerun()
    else:
        st.error("File Excel thiếu cột 'Tiếng Nga' hoặc 'Tiếng Việt'.")
