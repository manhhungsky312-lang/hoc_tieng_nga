import streamlit as st
import pandas as pd
import requests
import random

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Nga Ngữ Expert v32", layout="centered", page_icon="🇷🇺")

st.markdown("""
<style>
    .stApp { background-color: #f1f5f9; }
    .ques-box {
        background-color: #ffffff; padding: 25px; border-radius: 15px;
        border-left: 10px solid #e63946; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin: 20px 0;
    }
    .ques-vn { color: #1e293b; font-size: 30px !important; font-weight: 800; text-align: center; }
    b, strong { color: #dc2626; font-weight: bold; } 
    table { width: 100%; border-collapse: collapse; margin-top: 15px; background: white; }
    th { background-color: #1e3a8a; color: white; padding: 10px; border: 1px solid #cbd5e1; }
    td { border: 1px solid #cbd5e1; padding: 10px; font-size: 16px; }
</style>
""", unsafe_allow_html=True)

# --- 2. HÀM GỌI AI (SIÊU CHỈNH SỬA THUẬT NGỮ) ---
def call_ai_final(word_ru, word_vn):
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key: return "⚠️ Thiếu API Key."
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # PROMPT ÉP AI DÙNG THUẬT NGỮ CHUẨN VIỆT NAM
    prompt = f"""
    Phân tích từ: '{word_ru}' ({word_vn}).
    
    QUY ĐỊNH BẮT BUỘC:
    1. DANH TỪ: Phải xác định đúng Giống (Đực/Cái/Trung). Ví dụ 'Песня' phải là Giống Cái.
    2. TÊN 6 CÁCH: Phải ghi đúng thứ tự và tên tiếng Việt chuẩn sau:
       - Cách 1: Именительный (Danh cách)
       - Cách 2: Родительный (Sinh cách)
       - Cách 3: Дательный (Tặng cách)
       - Cách 4: Винительный (Đối cách)
       - Cách 5: Творительный (Cách công cụ)
       - Cách 6: Предложный (Cách giới từ)
    3. ĐỘNG TỪ: Chia 6 ngôi hiện tại, Quá khứ (4 dạng), Mệnh lệnh (2 dạng).
    4. TÍNH TỪ: Chia bảng 6 cách và Dạng ngắn đuôi.
    5. TRÌNH BÀY: Lập bảng Markdown, TÔ ĐẬM đuôi biến đổi bằng **.
    """
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Bạn là chuyên gia ngôn ngữ học Nga-Việt cấp cao. Bạn phải dùng thuật ngữ: Danh cách, Sinh cách, Tặng cách, Đối cách, Cách công cụ, Cách giới từ. Tuyệt đối không tự chế tên cách."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        return r.json()['choices'][0]['message']['content']
    except: return "⚠️ Hệ thống AI đang bảo trì, vui lòng thử lại."

# --- 3. QUẢN LÝ DỮ LIỆU (DÙNG CACHE CHỐNG LỖI FILE) ---
if 'pool' not in st.session_state: st.session_state.pool = []
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'status' not in st.session_state: st.session_state.status = None
if 'ai_res' not in st.session_state: st.session_state.ai_res = ""

# --- 4. SIDEBAR ---
with st.sidebar:
    st.header("🇷🇺 Cài đặt dữ liệu")
    f = st.file_uploader("Nạp file Excel (.xlsx)", type=["xlsx"])
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
        except: st.error("Lỗi định dạng file!")

# --- 5. GIAO DIỆN CHÍNH ---
st.title("Russian Expert v32")

if st.session_state.pool:
    curr = st.session_state.pool[st.session_state.idx]
    c_ru = next((k for k in curr.keys() if 'nga' in k or 'ru' in k), None)
    c_vn = next((k for k in curr.keys() if 'việt' in k or 'vn' in k), None)

    if c_ru and c_vn:
        w_ru, w_vn = str(curr[c_ru]).strip(), str(curr[c_vn]).strip()
        st.write(f"📊 Còn lại: **{len(st.session_state.pool)}** từ")
        
        st.markdown(f'<div class="ques-box"><div class="ques-vn">{w_vn}</div></div>', unsafe_allow_html=True)

        with st.form(key=f"f_{st.session_state.idx}"):
            u_in = st.text_input("Đáp án tiếng Nga:", value="")
            btn = st.form_submit_button("KIỂM TRA ✅")

        if btn:
            if u_in.strip().lower() == w_ru.lower():
                st.session_state.status = 'ok'
                st.success(f"⭐ CHÍNH XÁC: {w_ru}")
                st.session_state.ai_res = call_ai_final(w_ru, w_vn)
            else:
                st.session_state.status = 'err'
                st.error(f"❌ SAI! Đáp án đúng: {w_ru}")
                st.session_state.pool.append(curr)

        if st.session_state.status == 'ok' and st.session_state.ai_res:
            st.markdown("### 📚 PHÂN TÍCH CHUYÊN SÂU")
            st.markdown(st.session_state.ai_res)
            if st.button("Từ tiếp theo ➡️"):
                st.session_state.pool.pop(st.session_state.idx)
                if not st.session_state.pool: st.balloons()
                elif st.session_state.idx >= len(st.session_state.pool): st.session_state.idx = 0
                st.session_state.status, st.session_state.ai_res = None, ""
                st.rerun()
else:
    st.info("Mời nạp file Excel để bắt đầu.")
