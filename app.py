import streamlit as st
import pandas as pd
import requests
import random

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Nga Ngữ Expert v40.1", layout="centered", page_icon="🇷🇺")

st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    .stApp h1 { color: #1e3a8a; text-align: center; border-bottom: 3px solid #e63946; }
    .ques-box {
        background-color: #ffffff; padding: 25px; border-radius: 15px;
        border-left: 10px solid #e63946; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 20px 0;
    }
    .ques-vn { color: #1e293b; font-size: 32px !important; font-weight: 800; text-align: center; }
    b, strong { color: #dc2626; font-weight: bold; } 
    table { width: 100%; border-collapse: collapse; margin-top: 15px; background: white; }
    th { background-color: #f1f5f9; padding: 10px; border: 1px solid #cbd5e1; color: #1e3a8a; }
    td { border: 1px solid #cbd5e1; padding: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 2. HÀM GỌI AI ---
def call_ai_pro(word_ru, word_vn):
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key: return "⚠️ Thiếu API Key trong Secrets."
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    prompt = f"""
    Phân tích từ: '{word_ru}' ({word_vn}).
    - XÁC ĐỊNH GIỐNG: Kiểm tra đuôi. Ví dụ 'Песня' (-я) là Giống cái.
    - DANH TỪ: Chia 6 cách số ít & nhiều (Danh, Sinh, Tặng, Đối, Công cụ, Giới từ). Chuyển sang tính từ.
    - ĐỘNG TỪ: Chia 6 ngôi hiện tại; Quá khứ (4 dạng); Mệnh lệnh (ты, вы).
    - TÍNH TỪ: Chia 6 cách; Tính từ ngắn đuôi.
    - ĐẶT CÂU: 3 ví dụ tự nhiên (Nga - Việt).
    Tô đậm đuôi biến đổi bằng **.
    """
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Giáo viên tiếng Nga. Xác định giống chính xác 100%. Đặt câu tự nhiên."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        return r.json()['choices'][0]['message']['content']
    except: return "⚠️ AI đang bận."

# --- 3. KHỞI TẠO SESSION STATE (DÒNG 57 - ĐÃ FIX) ---
if 'pool' not in st.session_state:
    st.session_state.pool = []
if 'idx' not in st.session_state:
    st.session_state.idx = 0
if 'status' not in st.session_state:
    st.session_state.status = None
if 'ai_res' not in st.session_state:
    st.session_state.ai_res = ""

# --- 4. SIDEBAR ---
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1513326738677-b964603b136d?q=80&w=400", caption="🇷🇺 Nước Nga")
    f = st.file_uploader("Nạp file .xlsx", type=["xlsx"])
    if f:
        try:
            df = pd.read_excel(f, engine='openpyxl')
            df.columns = [str(c).strip().lower() for c in df.columns]
            if st.button("BẮT ĐẦU HỌC 🚀"):
                st.session_state.pool = df.to_dict('records')
                random.shuffle(st.session_state.pool)
                st.session_state.idx = 0
                st.session_state.status = None
                st.session_state.ai_res = ""
                st.rerun()
        except: st.error("Lỗi đọc file!")
    st.markdown("---")
    st.image("https://images.unsplash.com/photo-1504457047772-27fad17438e2?q=80&w=400", caption="🇻🇳 Việt Nam")

# --- 5. GIAO DIỆN CHÍNH ---
st.title("Russian Expert v40.1")

if st.session_state.pool:
    if st.session_state.idx >= len(st.session_state.pool):
        st.balloons()
        st.success("Hoàn thành bài học!")
        if st.button("Học lại từ đầu 🔄"):
            st.session_state.idx = 0
            st.rerun()
    else:
        curr = st.session_state.pool[st.session_state.idx]
        c_ru = next((k for k in curr.keys() if 'nga' in k or 'ru' in k), None)
        c_vn = next((k for k in curr.keys() if 'việt' in k or 'vn' in k), None)

        if c_ru and c_vn:
            w_ru, w_vn = str(curr[c_ru]).strip(), str(curr[c_vn]).strip()
            st.write(f"🔢 Câu: **{st.session_state.idx + 1}** / **{len(st.session_state.pool)}**")
            st.markdown(f'<div class="ques-box"><div class="ques-vn">{w_vn}</div></div>', unsafe_allow_html=True)

            with st.form(key=f"v40_form_{st.session_state.idx}"):
                u_in = st.text_input("Đáp án tiếng Nga:", value="")
                btn_check = st.form_submit_button("KIỂM TRA ✅")

            if btn_check:
                if u_in.strip().lower() == w_ru.lower():
                    st.session_state.status = 'ok'
                else:
                    st.session_state.status = 'err'
                    new_pos = min(st.session_state.idx + 3, len(st.session_state.pool))
                    st.session_state.pool.insert(new_pos, curr)
                
                with st.spinner("AI đang soạn bài học..."):
                    st.session_state.ai_res = call_ai_pro(w_ru, w_vn)

            if st.session_state.status == 'ok':
                st.success(f"⭐ CHÍNH XÁC: {w_ru}")
            elif st.session_state.status == 'err':
                st.error(f"❌ SAI! Đáp án đúng: {w_ru}")

            if st.session_state.ai_res:
                with st.expander("📚 PHÂN TÍCH NGỮ PHÁP & VÍ DỤ", expanded=True):
                    st.markdown(st.session_state.ai_res)
                if st.button("Câu tiếp theo ➡️"):
                    st.session_state.idx += 1
                    st.session_state.status = None
                    st.session_state.ai_res = ""
                    st.rerun()
        else: st.error("File thiếu cột Nga/Việt.")
else: st.info("Mời nạp file Excel ở thanh bên.")
