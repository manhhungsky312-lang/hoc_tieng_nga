import streamlit as st
import pandas as pd
import requests
import json
import random

# --- 1. CẤU HÌNH HỆ THỐNG ---
st.set_page_config(page_title="Học Tiếng Nga Chuyên Sâu v16", layout="centered")
api_key = st.secrets.get("GROQ_API_KEY")

def call_groq_pro(word_ru, word_vn):
    """Gọi AI để phân tích sâu, thêm tính từ và giới từ vào câu ví dụ"""
    if not api_key: return "⚠️ Thiếu GROQ_API_KEY."
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # PROMPT ĐÃ CẢI TIẾN: YÊU CẦU TÍNH TỪ VÀ GIỚI TỪ
    prompt = f"""
    Bạn là giảng viên tiếng Nga cao cấp. Phân tích từ: '{word_ru}' ({word_vn}).
    Yêu cầu:
    1. NGỮ PHÁP: Giống (Đực/Cái/Trung), chia Số ít/Số nhiều (Cách 1). 
       - Chú ý: Kiểm tra kỹ đuôi từ để xác định đúng giống.
    2. ĐỘNG TỪ ĐI KÈM: Nếu từ đó hay đi với động từ nào (ví dụ 'xem', 'ăn', 'đi'), hãy chia động từ đó ở 6 ngôi hiện tại.
    3. CÁCH DÙNG SINH ĐỘNG: Đặt 3 câu ví dụ (thay vì 2):
       - Câu 1: Dùng thêm TÍNH TỪ để miêu tả (Ví dụ: bộ phim 'hay', món ăn 'ngon').
       - Câu 2: Dùng thêm GIỚI TỪ (vị trí, thời gian, mục đích).
       - Câu 3: Một câu giao tiếp tự nhiên nhất của người bản xứ.
    (Tất cả ví dụ phải có tiếng Nga và dịch Việt sát nghĩa).
    """
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": "Bạn là chuyên gia ngôn ngữ Nga chuyên sâu."},
                     {"role": "user", "content": prompt}],
        "temperature": 0.5 # Tăng độ sáng tạo một chút cho câu văn sinh động
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        return response.json()['choices'][0]['message']['content']
    except:
        return "⚠️ AI hiện đang bận. Hãy xem đáp án và tiếp tục ôn tập."

# --- 2. LOGIC LẶP LẠI (SAI THÌ HỌC LẠI) ---
if 'pool' not in st.session_state: st.session_state.pool = [] 
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'status' not in st.session_state: st.session_state.status = None 

# --- 3. NẠP DỮ LIỆU ---
with st.sidebar:
    st.header("📂 Dữ liệu học tập")
    uploaded_file = st.file_uploader("Nạp file Excel", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        df.columns = [str(c).strip().lower() for c in df.columns]
        if not st.session_state.pool:
            st.session_state.pool = df.to_dict('records')
            random.shuffle(st.session_state.pool)
            st.session_state.idx = 0
            st.success("Đã nạp danh sách từ vựng!")

# --- 4. GIAO DIỆN HỌC ---
st.title("🇷🇺 Nga Ngữ Chuyên Sâu (Groq AI)")

if st.session_state.pool:
    current_word = st.session_state.pool[st.session_state.idx]
    c_ru = next((k for k in current_word.keys() if 'nga' in k or 'ru' in k), None)
    c_vn = next((k for k in current_word.keys() if 'việt' in k or 'vn' in k), None)

    if c_ru and c_vn:
        word_ru = str(current_word[c_ru]).strip()
        word_vn = str(current_word[c_vn]).strip()

        st.write(f"Số từ còn lại: **{len(st.session_state.pool)}**")
        st.markdown(f"### Dịch sang tiếng Nga: **{word_vn}**")

        # KHÓA FORM TRÁNH NHẢY CÂU
        with st.form(key=f"v16_form_{word_ru}_{st.session_state.idx}"):
            user_input = st.text_input("Gõ đáp án:", value="", key=f"input_{st.session_state.idx}")
            submit = st.form_submit_button("KIỂM TRA & PHÂN TÍCH 🔎")

        if submit:
            if user_input.strip().lower() == word_ru.lower():
                st.session_state.status = 'correct'
                st.success(f"⭐ CHÍNH XÁC! Đáp án: {word_ru}")
                with st.spinner("AI đang soạn bài học chuyên sâu..."):
                    st.markdown("---")
                    st.markdown(call_groq_pro(word_ru, word_vn))
            else:
                st.session_state.status = 'wrong'
                st.error(f"❌ SAI RỒI! Đáp án đúng: **{word_ru}**")
                st.info("Từ này sẽ được lặp lại ngẫu nhiên để bạn ghi nhớ.")
                # Nhét lại vào pool để học lại
                insert_pos = random.randint(st.session_state.idx + 1, len(st.session_state.pool)) if len(st.session_state.pool) > 1 else 1
                st.session_state.pool.insert(insert_pos, current_word)

        if st.session_state.status is not None:
            if st.button("Từ tiếp theo ➡️"):
                st.session_state.pool.pop(st.session_state.idx)
                if not st.session_state.pool:
                    st.success("Bạn đã hoàn thành danh sách!")
                elif st.session_state.idx >= len(st.session_state.pool):
                    st.session_state.idx = 0
                st.session_state.status = None
                st.rerun()
    else:
        st.error("File Excel thiếu cột Nga/Việt.")
else:
    st.info("Nạp file Excel ở bên trái để bắt đầu.")
