import streamlit as st
import pandas as pd
import requests
import random

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Nga Ngữ Expert v31", layout="centered", page_icon="🇷🇺")

st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    .stApp h1 { color: #1e3a8a; text-align: center; border-bottom: 3px solid #e63946; }
    .ques-box {
        background-color: #ffffff; padding: 25px; border-radius: 15px;
        border-left: 10px solid #e63946; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 20px 0;
    }
    .ques-vn { color: #1e293b; font-size: 30px !important; font-weight: 800; text-align: center; }
    b, strong { color: #dc2626; font-weight: bold; } 
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th { background-color: #f1f5f9; padding: 10px; border: 1px solid #cbd5e1; }
    td { border: 1px solid #cbd5e1; padding: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 2. HÀM ĐỌC FILE CÓ CACHE (CHỐNG LỖI FILE) ---
@st.cache_data
def load_data(file):
    try:
        df = pd.read_excel(file, engine='openpyxl')
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df.to_dict('records')
    except Exception as e:
        return str(e)

# --- 3. HÀM GỌI AI TOÀN DIỆN ---
def call_ai_pro(word_ru, word_vn):
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key: return "⚠️ Thiếu API Key trong Secrets."
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    prompt = f"""
    Phân tích từ: '{word_ru}' ({word_vn}).
    1. ĐỘNG TỪ: Chia 6 ngôi hiện tại; Quá khứ (đực, cái, trung, nhiều); Mệnh lệnh (ты, вы).
    2. DANH TỪ: Chia 6 cách số ít & số nhiều (Tên cách TIẾNG NGA); Chuyển sang tính từ.
    3. TÍNH TỪ: Chia 6 cách; Tính từ ngắn đuôi (Краткая форма).
    Lưu ý: Tô đậm đuôi biến đổi bằng **. 3 ví dụ Nga-Việt.
    """
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": "Chuyên gia Nga ngữ. Phân tích sâu hình thái từ. Không chia Cách cho Động từ."},
                     {"role": "user", "content": prompt}],
        "temperature": 0.1
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        return r.json()['choices'][0]['message']['content']
    except: return "⚠️ AI bận."

# --- 4. KHỞI TẠO SESSION STATE ---
if 'pool' not in st.session_state: st.session_state.pool = []
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'status' not in st.session_state: st.session_state.status = None
if 'ai_res' not in st.session_state: st.session_state.ai_res = ""

# --- 5. SIDEBAR ---
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1513326738677-b964603b136d?q=80&w=400")
    st.header("📂 Nạp Dữ Liệu")
    f = st.file_uploader("Chọn file .xlsx", type=["xlsx"])
    
    if f:
        data = load_data(f)
        if isinstance(data, str):
            st.error(f"Lỗi đọc file: {data}")
        else:
            if st.button("BẮT ĐẦU HỌC 🚀"):
                st.session_state.pool = data.copy()
                random.shuffle(st.session_state.pool)
                st.session_state.idx = 0
                st.session_state.status = None
                st.session_state.ai_res = ""
                st.rerun()

# --- 6. GIAO DIỆN CHÍNH ---
st.title("Russian Expert v31")

if st.session_state.pool:
    current = st.session_state.pool[st.session_state.idx]
    c_ru = next((k for k in current.keys() if 'nga' in k or 'ru' in k), None)
    c_vn = next((k for k in current.keys() if 'việt' in k or 'vn' in k), None)

    if c_ru and c_vn:
        word_ru, word_vn = str(current[c_ru]).strip(), str(current[c_vn]).strip()
        st.write(f"🔢 Từ còn lại: **{len(st.session_state.pool)}**")
        st.markdown(f'<div class="ques-box"><div class="ques-vn">{word_vn}</div></div>', unsafe_allow_html=True)

        # Form nhập liệu
        with st.form(key=f"form_{st.session_state.idx}"):
            u_in = st.text_input("Đáp án:", value="", placeholder="Gõ tiếng Nga...")
            btn = st.form_submit_button("KIỂM TRA ✅")

        if btn:
            if u_in.strip().lower() == word_ru.lower():
                st.session_state.status = 'ok'
                st.success(f"⭐ CHÍNH XÁC: {word_ru}")
                st.session_state.ai_res = call_ai_pro(word_ru, word_vn)
            else:
                st.session_state.status = 'err'
                st.error(f"❌ SAI! Đáp án đúng: {word_ru}")
                st.session_state.pool.append(current)

        if st.session_state.status == 'ok' and st.session_state.ai_res:
            with st.expander("📚 PHÂN TÍCH NGỮ PHÁP", expanded=True):
                st.markdown(st.session_state.ai_res)

        if st.session_state.status:
            if st.button("Từ tiếp theo ➡️"):
                st.session_state.pool.pop(st.session_state.idx)
                if not st.session_state.pool: st.balloons()
                elif st.session_state.idx >= len(st.session_state.pool): st.session_state.idx = 0
                st.session_state.status, st.session_state.ai_res = None, ""
                st.rerun()
    else: st.error("File thiếu cột Nga/Việt.")
else: st.info("Mời nạp file Excel ở thanh bên.")
