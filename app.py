import streamlit as st
import pandas as pd
import requests
import json
import random

# --- 1. CẤU HÌNH HỆ THỐNG ---
st.set_page_config(page_title="Học Tiếng Nga Thông Minh v12", layout="centered")

# Lấy API KEY từ Secrets
api_key = st.secrets.get("GEMINI_API_KEY")

def call_gemini_ai(word_ru, word_vn):
    """Cơ chế dò đường tự động để tránh lỗi 404"""
    if not api_key: 
        return "⚠️ Lỗi: Chưa cấu hình GEMINI_API_KEY trong Secrets của Streamlit."
    
    # Danh sách các địa chỉ API khả dụng của Google
    endpoints = [
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}",
        f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    ]
    
    prompt = f"""
    Hãy phân tích từ tiếng Nga: '{word_ru}' (nghĩa: {word_vn}).
    Yêu cầu trình bày tự nhiên, không máy móc:
    1. Ngữ pháp: Xác định Giống (Đực/Cái/Trung), chia số ít và số nhiều. (Nếu là động từ: chia 6 ngôi hiện tại).
    2. Cách dùng: Đặt 2 câu ví dụ ngắn gọn, đời thường mà người Nga hay nói (kèm dịch Việt).
    """
    
    payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.4}}
    
    last_status = 0
    for url in endpoints:
        try:
            response = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload), timeout=10)
            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text']
            last_status = response.status_code
        except:
            continue
            
    return f"❌ Vẫn gặp lỗi kết nối (Mã {last_status}). Có thể API Key của bạn bị sai hoặc chưa được kích hoạt Model tại Google AI Studio."

# --- 2. QUẢN LÝ BỘ NHỚ (PHƯƠNG PHÁP LẶP LẠI) ---
if 'pool' not in st.session_state: st.session_state.pool = [] 
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'status' not in st.session_state: st.session_state.status = None 

# --- 3. SIDEBAR: NẠP DỮ LIỆU ---
with st.sidebar:
    st.header("⚙️ Cài đặt")
    uploaded_file = st.file_uploader("Nạp file Excel vựng", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        df.columns = [str(c).strip().lower() for c in df.columns]
        
        if not st.session_state.pool:
            st.session_state.pool = df.to_dict('records')
            random.shuffle(st.session_state.pool)
            st.session_state.idx = 0
            st.session_state.status = None
            st.success("Đã nạp xong từ vựng!")

# --- 4. GIAO DIỆN HÀNH ĐỘNG ---
st.title("🇷🇺 Russian Smart Learning")

if st.session_state.pool:
    current_data = st.session_state.pool[st.session_state.idx]
    c_ru = next((k for k in current_data.keys() if 'nga' in k or 'ru' in k), None)
    c_vn = next((k for k in current_data.keys() if 'việt' in k or 'vn' in k), None)

    if c_ru and c_vn:
        word_ru_ans = str(current_data[c_ru]).strip()
        word_vn_ques = str(current_data[c_vn]).strip()

        st.write(f"Số từ còn lại: **{len(st.session_state.pool)}**")
        st.markdown(f"### Dịch sang tiếng Nga: **{word_vn_ques}**")

        # FORM KHÓA CHẶT ID CÂU HỎI
        form_key = f"form_{word_ru_ans}_{st.session_state.idx}"
        with st.form(key=form_key):
            user_input = st.text_input("Đáp án của bạn:", value="", key=f"input_{st.session_state.idx}")
            btn_submit = st.form_submit_button("KIỂM TRA ✅")

        if btn_submit:
            if user_input.strip().lower() == word_ru_ans.lower():
                st.session_state.status = 'correct'
                st.success(f"⭐ CHÍNH XÁC! Đáp án: {word_ru_ans}")
                with st.spinner("AI đang phân tích..."):
                    st.markdown("---")
                    st.markdown(call_gemini_ai(word_ru_ans, word_vn_ques))
            else:
                st.session_state.status = 'wrong'
                st.error(f"❌ SAI RỒI! Đáp án đúng là: **{word_ru_ans}**")
                st.info("Từ này sẽ được lặp lại ngẫu nhiên ở phía sau.")
                
                # THUẬT TOÁN LẶP LẠI
                if len(st.session_state.pool) > 1:
                    insert_pos = random.randint(st.session_state.idx + 1, len(st.session_state.pool))
                    st.session_state.pool.insert(insert_pos, current_data)
                else:
                    st.session_state.pool.append(current_data)

        if st.session_state.status is not None:
            if st.button("Từ tiếp theo ➡️"):
                st.session_state.pool.pop(st.session_state.idx)
                if not st.session_state.pool:
                    st.success("Hoàn thành bài học!")
                    st.balloons()
                elif st.session_state.idx >= len(st.session_state.pool):
                    st.session_state.idx = 0
                st.session_state.status = None
                st.rerun()
    else:
        st.error("File Excel sai định dạng cột.")
else:
    st.info("Hãy nạp file Excel ở thanh bên.")
