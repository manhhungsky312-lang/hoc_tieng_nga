import streamlit as st
import pandas as pd
import requests
import json
import random

# --- 1. CẤU HÌNH & GIAO DIỆN ---
st.set_page_config(page_title="Nga Ngữ Chuyên Sâu v22", layout="centered", page_icon="🇷🇺")

st.markdown("""
<style>
    .stApp h1 { color: #1e3a8a; text-align: center; border-bottom: 3px solid #e63946; }
    .ques-box { background-color: #ffffff; padding: 25px; border-radius: 15px; border-left: 8px solid #e63946; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin: 20px 0; }
    .ques-vn { color: #1e293b; font-size: 26px !important; font-weight: 800; }
    table { width: 100%; border-collapse: collapse; }
    th { background-color: #f1f5f9; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

api_key = st.secrets.get("GROQ_API_KEY")

def call_groq_v22(word_ru, word_vn):
    if not api_key: return "⚠️ Thiếu API Key."
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # PROMPT TỐI ƯU: KHÔNG RƯỜM RÀ, DÙNG TÊN CÁCH TIẾNG NGA
    prompt = f"""
    Phân tích từ tiếng Nga: '{word_ru}' ({word_vn}).
    
    YÊU CẦU TRÌNH BÀY (NGẮN GỌN, CHUẨN XÁC):
    1. NGỮ PHÁP: Chỉ nêu rõ Giống (Род) và Loại biến cách. KHÔNG liệt kê những gì từ đó không phải.
    2. BẢNG BIẾN CÁCH (Склонение): Lập bảng so sánh Số ít (Ед. ч.) và Số nhiều (Мн. ч.).
       - Tên các cách phải viết bằng TIẾNG NGA: Именительный (И.п.), Родительный (Р.п.), Дательный (Д.п.), Винительный (В.п.), Творительный (Т.п.), Предложный (П.п.).
    3. ĐỘNG TỪ LIÊN QUAN: Nếu là danh từ, gợi ý 1 động từ hay đi kèm và chia ở 6 ngôi (Я, Ты, Он/Она, Мы, Вы, Они).
    4. VÍ DỤ SINH ĐỘNG: 
       - 📝 Câu 1: Dùng Số ít + Tính từ miêu tả.
       - 🌍 Câu 2: Dùng Số nhiều + Giới từ.
       - 💬 Câu 3: Giao tiếp tự nhiên bản xứ.
    (Ví dụ có tiếng Nga và dịch Việt sát nghĩa).
    """
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Bạn là chuyên gia ngôn ngữ Nga. Trình bày súc tích, chuyên nghiệp, sử dụng thuật ngữ ngữ pháp bằng tiếng Nga."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        return response.json()['choices'][0]['message']['content']
    except: return "⚠️ AI bận. Hãy tiếp tục."

# --- 2. LOGIC LẬP LẠI ---
if 'pool' not in st.session_state: st.session_state.pool = [] 
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'status' not in st.session_state: st.session_state.status = None 
if 'ai_response' not in st.session_state: st.session_state.ai_response = ""

# --- 3. SIDEBAR ---
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1513326738677-b964603b136d?q=80&w=400", caption="🇷🇺 Moscow")
    uploaded_file = st.file_uploader("Nạp file Excel", type=["xlsx"])
    if uploaded_file and not st.session_state.pool:
        df = pd.read_excel(uploaded_file)
        df.columns = [str(c).strip().lower() for c in df.columns]
        st.session_state.pool = df.to_dict('records')
        random.shuffle(st.session_state.pool)
    st.image("https://images.unsplash.com/photo-1504457047772-27fad17438e2?q=80&w=400", caption="🇻🇳 Việt Nam")

# --- 4. GIAO DIỆN CHÍNH ---
st.title("🇷🇺 Chuyên Gia Nga Ngữ v22 🇻🇳")

if st.session_state.pool:
    current_word = st.session_state.pool[st.session_state.idx]
    c_ru = next((k for k in current_word.keys() if 'nga' in k or 'ru' in k), None)
    c_vn = next((k for k in current_word.keys() if 'việt' in k or 'vn' in k), None)

    if c_ru and c_vn:
        word_ru = str(current_word[c_ru]).strip()
        word_vn = str(current_word[c_vn]).strip()

        st.write(f"🔢 Số từ còn lại: **{len(st.session_state.pool)}**")
        st.markdown(f'<div class="ques-box"><div style="font-size:14px; color:#64748b;">DỊCH SANG TIẾNG NGA:</div><div class="ques-vn">{word_vn}</div></div>', unsafe_allow_html=True)

        with st.form(key=f"v22_form_{st.session_state.idx}"):
            user_input = st.text_input("Đáp án:", value="")
            submit = st.form_submit_button("KIỂM TRA & HIỆN BÀI HỌC ✅")

        if submit:
            if user_input.strip().lower() == word_ru.lower():
                st.session_state.status = 'correct'
                st.success(f"⭐ ĐÚNG! Đáp án: {word_ru}")
                with st.spinner("AI đang soạn bài học tối ưu..."):
                    st.session_state.ai_response = call_groq_v22(word_ru, word_vn)
            else:
                st.session_state.status = 'wrong'
                st.error(f"❌ SAI! Đáp án đúng: {word_ru}")
                insert_pos = random.randint(st.session_state.idx + 1, len(st.session_state.pool)) if len(st.session_state.pool) > 1 else 1
                st.session_state.pool.insert(insert_pos, current_word)

        if st.session_state.status == 'correct' and st.session_state.ai_response:
            with st.expander("📚 BÀI HỌC CHI TIẾT (SỐ ÍT & SỐ NHIỀU)", expanded=True):
                st.markdown(st.session_state.ai_response)

        if st.session_state.status is not None:
            if st.button("Từ tiếp theo ➡️"):
                st.session_state.pool.pop(st.session_state.idx)
                if not st.session_state.pool: st.balloons()
                elif st.session_state.idx >= len(st.session_state.pool): st.session_state.idx = 0
                st.session_state.status = None
                st.session_state.ai_response = ""
                st.rerun()
