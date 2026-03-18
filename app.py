import streamlit as st
import pandas as pd
import requests
import json
import random

# --- 1. CẤU HÌNH HỆ THỐNG & CSS CUSTOM (LÀM ĐẸP) ---
st.set_page_config(page_title="Nga Ngữ Chuyên Sâu v17 - Học Là Mê", layout="centered", page_icon="🇷🇺")

# Code CSS để làm đẹp giao diện
st.markdown("""
<style>
    /* Làm đẹp tiêu đề chính */
    .stApp h1 {
        color: #1E3A8A;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        text-align: center;
        border-bottom: 2px solid #E63946;
        padding-bottom: 10px;
    }
    /* Làm đẹp câu hỏi Tiếng Việt */
    .ques-box {
        background-color: #F1F5F9;
        padding: 20px;
        border-radius: 15px;
        border-left: 10px solid #E63946;
        margin-bottom: 20px;
    }
    .ques-vn {
        color: #111827;
        font-size: 24px !important;
        font-weight: bold;
    }
    /* Làm đẹp ô nhập liệu và nút bấm */
    .stTextInput input {
        border-radius: 10px !important;
        border: 2px solid #CBD5E1 !important;
    }
    .stButton button {
        border-radius: 10px !important;
        width: 100%;
        font-weight: bold;
    }
    /* Làm đẹp Sidebar */
    .css-163914f {
        background-color: #F8FAFC;
    }
</style>
""", unsafe_allow_html=True)

api_key = st.secrets.get("GROQ_API_KEY")

def call_groq_pro(word_ru, word_vn):
    """Gọi AI để phân tích sâu, thêm tính từ và giới từ vào câu ví dụ"""
    if not api_key: return "⚠️ Thiếu GROQ_API_KEY."
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # PROMPT CHUYÊN SÂU: YÊU CỰC KỲ CHI TIẾT
    prompt = f"""
    Bạn là giảng viên tiếng Nga cao cấp. Phân tích từ: '{word_ru}' ({word_vn}).
    Yêu cầu:
    1. NGỮ PHÁP (Có Emoji): Giống, chia Số ít/Số nhiều (Cách 1). 
    2. ĐỘNG TỪ ĐI KÈM: Tìm các động từ thường đi cùng từ này và chia ở 6 ngôi hiện tại.
    3. CÁCH DÙNG SINH ĐỘNG (Đây là phần quan trọng nhất, trình bày đẹp):
       - 📝 **Câu 1: Dùng thêm TÍNH TỪ** (Để miêu tả sinh động).
       - 🌍 **Câu 2: Dùng thêm GIỚI TỪ** (Vị trí, thời gian, phương hướng).
       - 💬 **Câu 3: Giao tiếp tự nhiên** (Cách người bản xứ nói hàng ngày).
    (Tất cả ví dụ phải có tiếng Nga và dịch Việt sát nghĩa).
    """
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": "Bạn là chuyên gia ngôn ngữ Nga chuyên sâu."},
                     {"role": "user", "content": prompt}],
        "temperature": 0.4
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

# --- 3. NẠP DỮ LIỆU & HÌNH ẢNH SIDEBAR ---
with st.sidebar:
    # 1. Hình ảnh Nước Nga (Nhà thờ Saint Basil)
    st.image("https://images.unsplash.com/photo-1512495039889-52a3b79872e6?q=80&w=400", caption="🇷🇺 Nước Nga Hùng Vĩ", use_column_width=True)
    
    st.header("📂 Cài đặt")
    uploaded_file = st.file_uploader("Chọn file Excel vựng", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        df.columns = [str(c).strip().lower() for c in df.columns]
        if not st.session_state.pool:
            st.session_state.pool = df.to_dict('records')
            random.shuffle(st.session_state.pool)
            st.session_state.idx = 0
            st.success("Đã nạp danh sách từ vựng!")
            
    # 2. Hình ảnh Việt Nam (Vịnh Hạ Long)
    st.image("https://images.unsplash.com/photo-1528126347108-08490326d16d?q=80&w=400", caption="🇻🇳 Việt Nam Quê Hương", use_column_width=True)

# --- 4. GIAO DIỆN HỌC CHÍNH ---
st.title("🇷🇺 Smart Russian Learning v17")

if st.session_state.pool:
    current_word = st.session_state.pool[st.session_state.idx]
    c_ru = next((k for k in current_data := current_word.keys() if 'nga' in k or 'ru' in k), None)
    c_vn = next((k for k in current_word.keys() if 'việt' in k or 'vn' in k), None)

    if c_ru and c_vn:
        word_ru = str(current_word[c_ru]).strip()
        word_vn = str(current_word[c_vn]).strip()

        st.write(f"🔢 Số từ còn lại: **{len(st.session_state.pool)}**")
        
        # Hộp câu hỏi Tiếng Việt (Dùng CSS Custom)
        st.markdown(f"""
        <div class="ques-box">
            <div style="font-size:16px; color:#64748B;">Dịch sang tiếng Nga:</div>
            <div class="ques-vn">{word_vn}</div>
        </div>
        """, unsafe_allow_html=True)

        # FORM KHÓA CHẶT ID CÂU HỎI
        with st.form(key=f"v17_form_{word_ru}_{st.session_state.idx}"):
            user_input = st.text_input("Gõ đáp án tiếng Nga của bạn:", value="", key=f"input_{st.session_state.idx}")
            submit = st.form_submit_button("KIỂM TRA & PHÂN TÍCH 🔎")

        if submit:
            if user_input.strip().lower() == word_ru.lower():
                st.session_state.status = 'correct'
                st.success(f"⭐ CHÍNH XÁC! Đáp án: **{word_ru}**")
                with st.spinner("AI đang soạn bài học chuyên sâu..."):
                    st.markdown("---")
                    # Dùng Expander để làm gọn phần phân tích
                    with st.expander("📚 Xem bài học chuyên sâu (Giống, Số, Cách, Ví dụ sống động)", expanded=True):
                        st.markdown(call_groq_pro(word_ru, word_vn))
            else:
                st.session_state.status = 'wrong'
                st.error(f"❌ SAI RỒI! Đáp án đúng: **{word_ru}**")
                st.info("💡 Từ này sẽ được lặp lại ngẫu nhiên để bạn ghi nhớ.")
                # Nhét lại vào pool để học lại
                insert_pos = random.randint(st.session_state.idx + 1, len(st.session_state.pool)) if len(st.session_state.pool) > 1 else 1
                st.session_state.pool.insert(insert_pos, current_word)

        if st.session_state.status is not None:
            if st.button("Học từ tiếp theo ➡️"):
                st.session_state.pool.pop(st.session_state.idx)
                if not st.session_state.pool:
                    st.success("Bạn đã hoàn thành danh sách!")
                    st.balloons()
                elif st.session_state.idx >= len(st.session_state.pool):
                    st.session_state.idx = 0
                st.session_state.status = None
                st.rerun()
    else:
        st.error("File Excel thiếu cột Nga/Việt.")
else:
    st.info("Mời nạp file Excel ở thanh bên để bắt đầu bài học.")
