import streamlit as st
import pandas as pd
import requests
import random

# --- 1. CẤU HÌNH ---
st.set_page_config(page_title="Nga Ngữ Expert v40.3", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    .ques-box {
        background-color: #ffffff; padding: 25px; border-radius: 15px;
        border-left: 10px solid #e63946; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 20px 0;
    }
    .ques-vn { color: #1e293b; font-size: 32px !important; font-weight: 800; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 2. HÀM AI ---
def call_ai_pro(word_ru, word_vn):
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key: return "⚠️ Thiếu API Key trong Secrets."
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    prompt = f"Phân tích từ: '{word_ru}' ({word_vn}). Xác định giống (ví dụ Песня là giống cái). Chia 6 cách danh từ (Danh, Sinh, Tặng, Đối, Công cụ, Giới từ), chia 6 ngôi động từ, đặt 3 ví dụ tự nhiên Nga-Việt. Tô đậm đuôi biến đổi bằng **."
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": "Giáo viên Nga ngữ chuyên nghiệp. Đặt câu tự nhiên."}, {"role": "user", "content": prompt}],
        "temperature": 0.1
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        return r.json()['choices'][0]['message']['content']
    except: return "⚠️ AI đang bận, bạn hãy thử lại sau ít giây."

# --- 3. KHỞI TẠO DỮ LIỆU ---
if 'pool' not in st.session_state: st.session_state.pool = []
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'status' not in st.session_state: st.session_state.status = None
if 'ai_res' not in st.session_state: st.session_state.ai_res = ""

# --- 4. THANH BÊN ---
with st.sidebar:
    st.header("📂 Nạp Dữ Liệu")
    f = st.file_uploader("Chọn file Excel (.xlsx)", type=["xlsx"])
    if f:
        try:
            df = pd.read_excel(f, engine='openpyxl')
            # Cảm biến tự động tìm cột:
            df.columns = [str(c).strip().lower() for c in df.columns]
            if st.button("BẮT ĐẦU HỌC 🚀"):
                st.session_state.pool = df.dropna(how='all').to_dict('records')
                random.shuffle(st.session_state.pool)
                st.session_state.idx = 0
                st.session_state.status, st.session_state.ai_res = None, ""
                st.rerun()
        except Exception as e:
            st.error(f"Lỗi đọc file: {e}")
    st.markdown("---")
    st.image("https://images.unsplash.com/photo-1513326738677-b964603b136d?q=80&w=200", caption="Học tốt nhé!")

# --- 5. GIAO DIỆN CHÍNH ---
st.title("Russian Expert v40.3")

if st.session_state.pool:
    if st.session_state.idx >= len(st.session_state.pool):
        st.balloons()
        st.success("Chúc mừng! Bạn đã thuộc hết từ vựng rồi.")
        if st.button("Học lại từ đầu 🔄"):
            st.session_state.idx = 0
            st.rerun()
    else:
        curr = st.session_state.pool[st.session_state.idx]
        # Tìm cột thông minh: chứa chữ 'nga'/'ru' và 'việt'/'vn'
        c_ru = next((k for k in curr.keys() if any(x in k for x in ['nga', 'ru'])), None)
        c_vn = next((k for k in curr.keys() if any(x in k for x in ['việt', 'vn'])), None)

        if c_ru and c_vn:
            w_ru, w_vn = str(curr[c_ru]).strip(), str(curr[c_vn]).strip()
            st.write(f"🔢 Từ số: **{st.session_state.idx + 1}** / **{len(st.session_state.pool)}**")
            st.markdown(f'<div class="ques-box"><div class="ques-vn">{w_vn}</div></div>', unsafe_allow_html=True)

            with st.form(key=f"f_{st.session_state.idx}"):
                u_in = st.text_input("Đáp án tiếng Nga:", value="", placeholder="Gõ từ...")
                btn = st.form_submit_button("KIỂM TRA ✅")

            if btn:
                if u_in.strip().lower() == w_ru.lower():
                    st.session_state.status = 'ok'
                else:
                    st.session_state.status = 'err'
                    # Chèn lại từ sai để học lại sau 2 câu nữa
                    st.session_state.pool.insert(st.session_state.idx + 3, curr)
                with st.spinner("Đợi AI phân tích ngữ pháp..."):
                    st.session_state.ai_res = call_ai_pro(w_ru, w_vn)

            if st.session_state.status == 'ok': st.success(f"⭐ ĐÚNG: {w_ru}")
            elif st.session_state.status == 'err': st.error(f"❌ SAI! Đáp án đúng: {w_ru}")

            if st.session_state.ai_res:
                with st.expander("📚 GIẢI THÍCH & ĐẶT CÂU", expanded=True):
                    st.markdown(st.session_state.ai_res)
                if st.button("Từ tiếp theo ➡️"):
                    st.session_state.idx += 1
                    st.session_state.status, st.session_state.ai_res = None, ""
                    st.rerun()
        else:
            st.error("Lỗi: File Excel của bạn phải có tiêu đề cột là 'Nga' và 'Việt'.")
else:
    st.info("Chào bạn! Hãy nạp file Excel ở bên trái để bắt đầu.")
