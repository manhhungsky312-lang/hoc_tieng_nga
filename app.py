import streamlit as st
import pandas as pd
import requests
import json
import random

# --- 1. CẤU HÌNH HỆ THỐNG ---
st.set_page_config(page_title="Học Tiếng Nga với DeepSeek", layout="centered")

# Lấy API KEY từ Secrets (Bạn đặt tên là DEEPSEEK_API_KEY trong Streamlit)
api_key = st.secrets.get("DEEPSEEK_API_KEY")

def call_deepseek_ai(word_ru, word_vn):
    """Gọi DeepSeek để phân tích ngữ pháp và đặt câu tự nhiên"""
    if not api_key: 
        return "⚠️ Lỗi: Chưa cấu hình DEEPSEEK_API_KEY trong Secrets."
    
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    prompt = f"""
    Bạn là chuyên gia ngôn ngữ Nga. Phân tích từ: '{word_ru}' ({word_vn}).
    1. Ngữ pháp: Giống (Đực/Cái/Trung), chia số ít/nhiều. (Động từ: chia 6 ngôi hiện tại).
    2. Cách dùng: Đặt 2 câu ví dụ ngắn gọn, tự nhiên như người Nga nói hàng ngày (kèm dịch Việt).
    Yêu cầu: Trình bày rõ ràng, không máy móc.
    """
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Bạn là trợ lý học tiếng Nga chuyên nghiệp."},
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=20)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"❌ Lỗi DeepSeek (Mã {response.status_code}). Kiểm tra lại API Key hoặc số dư tài khoản."
    except Exception as e:
        return f"⚠️ Không kết nối được DeepSeek: {str(e)}"

# --- 2. QUẢN LÝ BỘ NHỚ (PHƯƠNG PHÁP LẶP LẠI) ---
if 'pool' not in st.session_state: st.session_state.pool = [] 
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'status' not in st.session_state: st.session_state.status = None 

# --- 3. NẠP DỮ LIỆU ---
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
            st.success("Đã nạp và xáo trộn từ vựng!")

# --- 4. GIAO DIỆN HÀNH ĐỘNG ---
st.title("🇷🇺 Russian Learning (DeepSeek AI)")

if st.session_state.pool:
    current_data = st.session_state.pool[st.session_state.idx]
    c_ru = next((k for k in current_data.keys() if 'nga' in k or 'ru' in k), None)
    c_vn = next((k for k in current_data.keys() if 'việt' in k or 'vn' in k), None)

    if c_ru and c_vn:
        word_ru_ans = str(current_data[c_ru]).strip()
        word_vn_ques = str(current_data[c_vn]).strip()

        st.write(f"Số từ còn lại trong danh sách: **{len(st.session_state.pool)}**")
        st.markdown(f"### Dịch sang tiếng Nga: <span style='color:#E63946'>{word_vn_ques}</span>", unsafe_allow_html=True)

        # KHÓA FORM TRÁNH NHẢY CÂU (Sử dụng ID của từ làm Key)
        form_key = f"form_{word_ru_ans}_{st.session_state.idx}"
        with st.form(key=form_key):
            user_input = st.text_input("Đáp án của bạn:", value="", key=f"input_{st.session_state.idx}")
            btn_submit = st.form_submit_button("KIỂM TRA ✅")

        if btn_submit:
            if user_input.strip().lower() == word_ru_ans.lower():
                st.session_state.status = 'correct'
                st.success(f"⭐ CHÍNH XÁC! Đáp án: {word_ru_ans}")
                with st.spinner("DeepSeek đang phân tích..."):
                    explanation = call_deepseek_ai(word_ru_ans, word_vn_ques)
                    st.markdown("---")
                    st.markdown(explanation)
            else:
                st.session_state.status = 'wrong'
                st.error(f"❌ SAI RỒI! Đáp án đúng là: **{word_ru_ans}**")
                st.info("Từ này sẽ được lặp lại ngẫu nhiên ở phía sau để bạn ghi nhớ.")
                
                # THUẬT TOÁN LẶP LẠI: Chèn vào vị trí ngẫu nhiên phía sau idx hiện tại
                if len(st.session_state.pool) > 1:
                    insert_pos = random.randint(st.session_state.idx + 1, len(st.session_state.pool))
                    st.session_state.pool.insert(insert_pos, current_data)
                else:
                    st.session_state.pool.append(current_data)

        if st.session_state.status is not None:
            if st.button("Từ tiếp theo ➡️"):
                st.session_state.pool.pop(st.session_state.idx)
                if not st.session_state.pool:
                    st.success("Hoàn thành tất cả từ vựng!")
                    st.balloons()
                elif st.session_state.idx >= len(st.session_state.pool):
                    st.session_state.idx = 0
                st.session_state.status = None
                st.rerun()
    else:
        st.error("File Excel không tìm thấy cột 'Tiếng Nga' hoặc 'Tiếng Việt'.")
else:
    st.info("Hãy nạp file Excel ở thanh bên để bắt đầu.")
