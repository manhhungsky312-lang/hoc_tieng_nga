import streamlit as st
import pandas as pd
import requests
import json
import random

# --- 1. CẤU HÌNH HỆ THỐNG ---
st.set_page_config(page_title="Học Tiếng Nga Thông Minh v10", layout="centered")
api_key = st.secrets.get("GEMINI_API_KEY")

def call_gemini_analyze(word_ru, word_vn):
    """Chỉ gọi AI khi người học trả lời ĐÚNG để phân tích sâu"""
    if not api_key: return "Thiếu API Key."
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    prompt = f"""
    Phân tích từ tiếng Nga: '{word_ru}' (nghĩa: {word_vn}).
    Yêu cầu:
    1. Xác định Giống (Đực/Cái/Trung) dựa trên đuôi từ số ít, chia số ít/nhiều.
    2. Nếu là động từ, chia 6 ngôi hiện tại.
    3. Đặt 2 câu ví dụ cực kỳ tự nhiên, đời thường mà người Nga hay dùng (kèm dịch Việt).
    Lưu ý: Trình bày rõ ràng, dễ hiểu.
    """
    
    payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.2}}
    try:
        response = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except: return "AI đang bận, hãy xem đáp án và tiếp tục."

# --- 2. QUẢN LÝ BỘ NHỚ ---
if 'pool' not in st.session_state: st.session_state.pool = [] # Danh sách câu hỏi hiện tại
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'status' not in st.session_state: st.session_state.status = None # 'correct', 'wrong', None

# --- 3. SIDEBAR: NẠP DỮ LIỆU ---
with st.sidebar:
    st.header("📂 Dữ liệu học tập")
    file = st.file_uploader("Nạp file Excel", type=["xlsx"])
    if file:
        df = pd.read_excel(file)
        df.columns = [str(c).strip().lower() for c in df.columns]
        # Chuyển dataframe thành list các dictionary để dễ xáo trộn
        if not st.session_state.pool:
            st.session_state.pool = df.to_dict('records')
            random.shuffle(st.session_state.pool)
            st.session_state.idx = 0
            st.success("Đã nạp dữ liệu thành công!")

# --- 4. GIAO DIỆN CHÍNH ---
st.title("🇷🇺 Russian Smart Learning")

if st.session_state.pool:
    current_word = st.session_state.pool[st.session_state.idx]
    
    # Tìm cột Nga/Việt tự động
    c_ru = next((k for k in current_word.keys() if 'nga' in k or 'ru' in k), None)
    c_vn = next((k for k in current_word.keys() if 'việt' in k or 'vn' in k), None)

    if c_ru and c_vn:
        word_ru = str(current_row := current_word[c_ru]).strip()
        word_vn = str(current_word[c_vn]).strip()

        st.write(f"Câu hỏi còn lại trong danh sách: {len(st.session_state.pool)}")
        st.subheader(f"Dịch sang tiếng Nga: {word_vn}")

        # KHÓA FORM THEO TỪ HIỆN TẠI (CHỐNG NHẢY CÂU)
        with st.form(key=f"form_{word_ru}_{st.session_state.idx}"):
            user_input = st.text_input("Đáp án của bạn:", value="", key=f"input_{st.session_state.idx}")
            submit = st.form_submit_button("KIỂM TRA ✅")

        if submit:
            if user_input.strip().lower() == word_ru.lower():
                st.session_state.status = 'correct'
                st.success(f"⭐ CHÍNH XÁC! Đáp án: {word_ru}")
                with st.spinner("AI đang phân tích ngữ pháp tự nhiên..."):
                    st.markdown("---")
                    st.markdown(call_gemini_analyze(word_ru, word_vn))
            else:
                st.session_state.status = 'wrong'
                st.error(f"❌ SAI RỒI! Đáp án đúng là: {word_ru}")
                st.info("Từ này sẽ được lặp lại ngẫu nhiên ở các câu sau để bạn ghi nhớ.")
                
                # THUẬT TOÁN LẶP LẠI: Chèn từ sai vào một vị trí ngẫu nhiên phía sau
                if len(st.session_state.pool) > 1:
                    insert_pos = random.randint(st.session_state.idx + 1, len(st.session_state.pool))
                    st.session_state.pool.insert(insert_pos, current_word)
                else:
                    st.session_state.pool.append(current_word)

        # ĐIỀU HƯỚNG
        if st.session_state.status is not None:
            if st.button("Từ tiếp theo ➡️"):
                # Xóa từ vừa làm xong (nếu muốn làm tiếp câu mới)
                st.session_state.pool.pop(st.session_state.idx)
                
                # Nếu hết hàng thì quay về 0, nếu không thì giữ idx cũ (vì pop đã đôn từ dưới lên)
                if not st.session_state.pool:
                    st.warning("Chúc mừng! Bạn đã hoàn thành tất cả các từ.")
                    st.balloons()
                
                if st.session_state.idx >= len(st.session_state.pool):
                    st.session_state.idx = 0
                
                st.session_state.status = None
                st.rerun()
    else:
        st.error("File Excel không đúng định dạng cột Nga/Việt.")
else:
    st.info("Hãy nạp file Excel ở thanh bên để bắt đầu bài học.")
