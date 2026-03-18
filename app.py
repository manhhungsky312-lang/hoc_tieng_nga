import streamlit as st
import pandas as pd
import requests
import json
import random

# --- 1. CẤU HÌNH HỆ THỐNG ---
st.set_page_config(page_title="Học Tiếng Nga Thông Minh v11", layout="centered")

# Lấy API KEY từ Secrets
api_key = st.secrets.get("GEMINI_API_KEY")

def call_gemini_ai(word_ru, word_vn):
    """Gọi Gemini phân tích sâu khi người học trả lời ĐÚNG"""
    if not api_key: 
        return "⚠️ Lỗi: Chưa cấu hình GEMINI_API_KEY trong Secrets của Streamlit."
    
    # Thử gọi qua v1beta (thường ổn định hơn cho tài khoản cá nhân)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    prompt = f"""
    Phân tích từ tiếng Nga: '{word_ru}' (nghĩa: {word_vn}).
    Trình bày ngắn gọn, chính xác:
    1. Ngữ pháp: Giống (Đực/Cái/Trung), chia số ít/nhiều. (Nếu là động từ: chia 6 ngôi hiện tại).
    2. Cách dùng tự nhiên: Đặt 2 câu ví dụ ngắn, đời thường mà người Nga hay nói (kèm dịch Việt).
    Lưu ý: Không dùng ngôn ngữ quá trang trọng hay quân sự máy móc.
    """
    
    payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.3}}
    try:
        response = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload), timeout=15)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"❌ Lỗi kết nối AI (Mã {response.status_code}). Hãy kiểm tra lại API Key."
    except:
        return "⚠️ AI hiện đang bận hoặc có sự cố đường truyền. Bạn hãy tiếp tục học từ tiếp theo."

# --- 2. QUẢN LÝ BỘ NHỚ (PHƯƠNG PHÁP LẶP LẠI) ---
if 'pool' not in st.session_state: st.session_state.pool = [] 
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'status' not in st.session_state: st.session_state.status = None 

# --- 3. NẠP DỮ LIỆU ---
with st.sidebar:
    st.header("📂 Cài đặt")
    uploaded_file = st.file_uploader("Nạp file Excel vựng", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        df.columns = [str(c).strip().lower() for c in df.columns]
        
        # Nếu chưa có danh sách câu hỏi thì mới nạp để tránh reset giữa chừng
        if not st.session_state.pool:
            st.session_state.pool = df.to_dict('records')
            random.shuffle(st.session_state.pool)
            st.session_state.idx = 0
            st.session_state.status = None
            st.success("Đã nạp và xáo trộn từ vựng!")

# --- 4. GIAO DIỆN HÀNH ĐỘNG ---
st.title("🇷🇺 Russian Smart Learning")

if st.session_state.pool:
    # Lấy từ hiện tại dựa trên idx
    current_data = st.session_state.pool[st.session_state.idx]
    
    # Tìm cột tự động
    c_ru = next((k for k in current_data.keys() if 'nga' in k or 'ru' in k), None)
    c_vn = next((k for k in current_data.keys() if 'việt' in k or 'vn' in k), None)

    if c_ru and c_vn:
        word_ru_ans = str(current_data[c_ru]).strip()
        word_vn_ques = str(current_data[c_vn]).strip()

        st.write(f"Số từ còn lại trong danh sách: **{len(st.session_state.pool)}**")
        st.markdown(f"### Dịch sang tiếng Nga: <span style='color:#007BFF'>{word_vn_ques}</span>", unsafe_allow_html=True)

        # FORM ĐỂ KHÓA ID CÂU HỎI (CHỐNG NHẢY CÂU)
        form_key = f"form_{word_ru_ans}_{st.session_state.idx}"
        with st.form(key=form_key):
            user_input = st.text_input("Đáp án của bạn:", value="")
            btn_submit = st.form_submit_button("KIỂM TRA ✅")

        if btn_submit:
            if user_input.strip().lower() == word_ru_ans.lower():
                st.session_state.status = 'correct'
                st.success(f"⭐ CHÍNH XÁC! Đáp án: {word_ru_ans}")
                with st.spinner("AI đang phân tích từ vựng..."):
                    explanation = call_gemini_ai(word_ru_ans, word_vn_ques)
                    st.markdown("---")
                    st.markdown(explanation)
            else:
                st.session_state.status = 'wrong'
                st.error(f"❌ SAI RỒI! Đáp án đúng phải là: **{word_ru_ans}**")
                st.info("Từ này sẽ được lặp lại ngẫu nhiên ở các câu sau.")
                
                # THUẬT TOÁN LẶP LẠI: Chèn từ sai vào vị trí ngẫu nhiên phía sau
                if len(st.session_state.pool) > 1:
                    insert_pos = random.randint(st.session_state.idx + 1, len(st.session_state.pool))
                    st.session_state.pool.insert(insert_pos, current_data)
                else:
                    st.session_state.pool.append(current_data)

        # NÚT ĐIỀU HƯỚNG
        if st.session_state.status is not None:
            if st.button("Từ tiếp theo ➡️"):
                # Loại bỏ từ hiện tại sau khi đã làm xong (dù đúng hay sai)
                st.session_state.pool.pop(st.session_state.idx)
                
                if not st.session_state.pool:
                    st.success("Hoàn thành tất cả từ vựng!")
                    st.balloons()
                    st.session_state.pool = []
                else:
                    # Nếu idx vượt quá độ dài mới thì quay về 0
                    if st.session_state.idx >= len(st.session_state.pool):
                        st.session_state.idx = 0
                
                st.session_state.status = None
                st.rerun()
    else:
        st.error("File Excel không tìm thấy cột 'Tiếng Nga' hoặc 'Tiếng Việt'.")
else:
    st.info("Hãy nạp file Excel ở thanh bên để bắt đầu.")
