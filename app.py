import streamlit as st
import pandas as pd
import requests
import json
import random

# --- 1. CẤU HÌNH HỆ THỐNG & LÀM ĐẸP (CSS) ---
st.set_page_config(page_title="Học Tiếng Nga v18", layout="centered", page_icon="🇷🇺")

# CSS để tạo hộp câu hỏi và làm đẹp giao diện
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
    .ques-vn { color: #1e293b; font-size: 26px !important; font-weight: 800; }
    .stButton button { border-radius: 12px !important; font-weight: bold; transition: 0.3s; }
    .stButton button:hover { transform: scale(1.02); background-color: #e63946 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

api_key = st.secrets.get("GROQ_API_KEY")

def call_groq_pro(word_ru, word_vn):
    """Gọi AI phân tích sâu với tính từ và giới từ"""
    if not api_key: return "⚠️ Thiếu GROQ_API_KEY trong Secrets."
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    prompt = f"""
    Bạn là giảng viên tiếng Nga. Phân tích từ: '{word_ru}' ({word_vn}).
    Yêu cầu trình bày đẹp, có emoji:
    1. NGỮ PHÁP: Giống (Đực/Cái/Trung), chia Số ít/Số nhiều. (Động từ: chia 6 ngôi hiện tại).
    2. CÁCH DÙNG SINH ĐỘNG: Đặt 3 câu ví dụ:
       - 📝 Câu 1: Dùng thêm TÍNH TỪ miêu tả.
       - 🌍 Câu 2: Dùng thêm GIỚI TỪ (vị trí, thời gian).
       - 💬 Câu 3: Cách nói tự nhiên của người Nga.
    (Tất cả có tiếng Nga và dịch Việt sát nghĩa).
    """
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": "Chuyên gia ngôn ngữ Nga."},
                     {"role": "user", "content": prompt}],
        "temperature": 0.5
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        return response.json()['choices'][0]['message']['content']
    except:
        return "⚠️ AI bận. Hãy tiếp tục học từ tiếp theo."

# --- 2. QUẢN LÝ BỘ NHỚ ---
if 'pool' not in st.session_state: st.session_state.pool = [] 
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'status' not in st.session_state: st.session_state.status = None 

# --- 3. SIDEBAR (HÌNH ẢNH NGA - VIỆT) ---
with st.sidebar:
    # Hình ảnh Điện Kremlin - Nga
    st.image("https://images.unsplash.com/photo-1513326738677-b964603b136d?q=80&w=400", caption="🇷🇺 Nước Nga Hùng Vĩ")
    
    st.header("📂 Dữ liệu học tập")
    uploaded_file = st.file_uploader("Nạp file Excel vựng", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        df.columns = [str(c).strip().lower() for c in df.columns]
        if not st.session_state.pool:
            st.session_state.pool = df.to_dict('records')
            random.shuffle(st.session_state.pool)
            st.session_state.idx = 0
            st.success("Đã nạp dữ liệu!")
            
    # Hình ảnh Ruộng bậc thang - Việt Nam
    st.image("https://images.unsplash.com/photo-1504457047772-27fad17438e2?q=80&w=400", caption="🇻🇳 Việt Nam Quê Hương")

# --- 4. GIAO DIỆN CHÍNH ---
st.title("🇷🇺 Russian Expert v18 🇻🇳")

if st.session_state.pool:
    # Lấy dữ liệu an toàn
    current_word = st.session_state.pool[st.session_state.idx]
    
    # Tìm cột Nga/Việt
    c_ru = next((k for k in current_word.keys() if 'nga' in k or 'ru' in k), None)
    c_vn = next((k for k in current_word.keys() if 'việt' in k or 'vn' in k), None)

    if c_ru and c_vn:
        word_ru = str(current_word[c_ru]).strip()
        word_vn = str(current_word[c_vn]).strip()

        st.write(f"🔢 Từ thứ: **{st.session_state.idx + 1}** | Còn lại: **{len(st.session_state.pool)}**")
        
        # Hộp câu hỏi
        st.markdown(f"""
        <div class="ques-box">
            <div style="font-size:15px; color:#64748b; font-weight:bold;">DỊCH SANG TIẾNG NGA:</div>
            <div class="ques-vn">{word_vn}</div>
        </div>
        """, unsafe_allow_html=True)

        # FORM KHÓA ID
        with st.form(key=f"v18_form_{st.session_state.idx}"):
            user_input = st.text_input("Nhập từ tiếng Nga:", value="", placeholder="Gõ vào đây...")
            submit = st.form_submit_button("KIỂM TRA ✅")

        if submit:
            if user_input.strip().lower() == word_ru.lower():
                st.session_state.status = 'correct'
                st.success(f"⭐ CHÍNH XÁC! Đáp án: **{word_ru}**")
                with st.spinner("AI đang soạn bài học..."):
                    with st.expander("📚 XEM PHÂN TÍCH CHI TIẾT", expanded=True):
                        st.markdown(call_groq_pro(word_ru, word_vn))
            else:
                st.session_state.status = 'wrong'
                st.error(f"❌ SAI RỒI! Đáp án đúng: **{word_ru}**")
                st.info("💡 Từ này sẽ xuất hiện lại ngẫu nhiên để bạn ôn tập.")
                
                # Logic lặp lại: Nhét từ vào vị trí ngẫu nhiên phía sau
                if len(st.session_state.pool) > 1:
                    insert_pos = random.randint(st.session_state.idx + 1, len(st.session_state.pool))
                    st.session_state.pool.insert(insert_pos, current_word)
                else:
                    st.session_state.pool.append(current_word)

        if st.session_state.status is not None:
            if st.button("Học từ tiếp theo ➡️"):
                st.session_state.pool.pop(st.session_state.idx)
                if not st.session_state.pool:
                    st.balloons()
                    st.success("Hoàn thành bài học!")
                elif st.session_state.idx >= len(st.session_state.pool):
                    st.session_state.idx = 0
                st.session_state.status = None
                st.rerun()
    else:
        st.error("File Excel thiếu cột 'Tiếng Nga' hoặc 'Tiếng Việt'.")
else:
    st.info("Mời bạn nạp file Excel ở thanh bên để bắt đầu.")
