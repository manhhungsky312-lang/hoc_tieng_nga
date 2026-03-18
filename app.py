import streamlit as st
import pandas as pd
import requests
import json
import random

# --- 1. GIAO DIỆN & STYLE ---
st.set_page_config(page_title="Nga Ngữ Chuyên Sâu v20", layout="centered", page_icon="🇷🇺")

st.markdown("""
<style>
    .stApp h1 { color: #1e3a8a; text-align: center; border-bottom: 3px solid #e63946; }
    .ques-box { background-color: #ffffff; padding: 25px; border-radius: 15px; border-left: 8px solid #e63946; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin: 20px 0; }
    .ques-vn { color: #1e293b; font-size: 26px !important; font-weight: 800; }
    .report-btn { color: #ef4444; font-size: 12px; cursor: pointer; text-decoration: underline; }
</style>
""", unsafe_allow_html=True)

api_key = st.secrets.get("GROQ_API_KEY")

def call_groq_v20(word_ru, word_vn, force_recheck=False):
    """Gọi AI với cơ chế kiểm tra ngoại lệ và bất quy tắc"""
    if not api_key: return "⚠️ Thiếu API Key."
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    instruction = "Bạn là một từ điển bách khoa tiếng Nga."
    if force_recheck:
        instruction += " NGƯỜI DÙNG BÁO BẠN ĐÃ SAI. Hãy kiểm tra lại các trường hợp bất quy tắc, giống đặc biệt hoặc chia động từ ngoại lệ."

    prompt = f"""
    Phân tích từ: '{word_ru}' ({word_vn}).
    
    BẮT BUỘC KIỂM TRA:
    1. NGOẠI LỆ: Từ này có phải từ mượn không biến cách? Có phải giống đực đuôi -а/-я (như Папа, Мужчина)? Có phải giống trung đặc biệt (như Имя, Время)? 
    2. ĐỘNG TỪ: Nếu là động từ bất quy tắc (như Хотеть, Идти), hãy chia thật chính xác 6 ngôi.
    3. TRÌNH BÀY:
       - 📕 NGỮ PHÁP: Giống, Số, Cách (Giải thích nếu là từ đặc biệt).
       - 🔄 CHIA TỪ: 6 ngôi (nếu là động từ) hoặc Biến cách (nếu là danh từ khó).
       - 🌟 VÍ DỤ SINH ĐỘNG: 
         + Câu 1 (+Tính từ miêu tả).
         + Câu 2 (+Giới từ chỉ vị trí/thời gian).
         + Câu 3 (Giao tiếp tự nhiên bản xứ).
    """
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": instruction}, {"role": "user", "content": prompt}],
        "temperature": 0.1 # Mức độ cực kỳ thấp để tránh AI 'tự chế'
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        return response.json()['choices'][0]['message']['content']
    except: return "⚠️ AI bận. Hãy tiếp tục."

# --- 2. LOGIC LẶP LẠI ---
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
st.title("🇷🇺 Chuyên Gia Nga Ngữ v20 🇻🇳")

if st.session_state.pool:
    current_word = st.session_state.pool[st.session_state.idx]
    c_ru = next((k for k in current_word.keys() if 'nga' in k or 'ru' in k), None)
    c_vn = next((k for k in current_word.keys() if 'việt' in k or 'vn' in k), None)

    if c_ru and c_vn:
        word_ru = str(current_word[c_ru]).strip()
        word_vn = str(current_word[c_vn]).strip()

        st.write(f"🔢 Số từ còn lại: **{len(st.session_state.pool)}**")
        st.markdown(f'<div class="ques-box"><div style="font-size:14px; color:#64748b;">DỊCH SANG TIẾNG NGA:</div><div class="ques-vn">{word_vn}</div></div>', unsafe_allow_html=True)

        with st.form(key=f"v20_form_{st.session_state.idx}"):
            user_input = st.text_input("Đáp án:", value="")
            submit = st.form_submit_button("KIỂM TRA ✅")

        if submit:
            if user_input.strip().lower() == word_ru.lower():
                st.session_state.status = 'correct'
                st.success(f"⭐ ĐÚNG! Đáp án: {word_ru}")
                with st.spinner("AI đang tra cứu ngoại lệ..."):
                    st.session_state.ai_response = call_groq_v20(word_ru, word_vn)
            else:
                st.session_state.status = 'wrong'
                st.error(f"❌ SAI! Đáp án: {word_ru}")
                # Lặp lại từ sai
                insert_pos = random.randint(st.session_state.idx + 1, len(st.session_state.pool)) if len(st.session_state.pool) > 1 else 1
                st.session_state.pool.insert(insert_pos, current_word)

        # Hiển thị kết quả AI và Nút Báo Lỗi
        if st.session_state.status == 'correct' and st.session_state.ai_response:
            with st.expander("📚 PHÂN TÍCH CHUYÊN SÂU", expanded=True):
                st.markdown(st.session_state.ai_response)
                if st.button("🚩 AI NÓI SAI? BẮT AI KIỂM TRA LẠI"):
                    with st.spinner("Đang tra cứu lại nguồn dữ liệu chuẩn..."):
                        st.session_state.ai_response = call_groq_v20(word_ru, word_vn, force_recheck=True)
                        st.rerun()

        if st.session_state.status is not None:
            if st.button("Từ tiếp theo ➡️"):
                st.session_state.pool.pop(st.session_state.idx)
                if not st.session_state.pool: st.balloons()
                elif st.session_state.idx >= len(st.session_state.pool): st.session_state.idx = 0
                st.session_state.status = None
                st.session_state.ai_response = ""
                st.rerun()
