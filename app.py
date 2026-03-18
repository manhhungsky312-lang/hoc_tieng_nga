import streamlit as st
import pandas as pd
import requests
import random

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Nga Ngữ Expert v40.4", layout="centered", page_icon="🇷🇺")

st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
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

# --- 2. HÀM GỌI AI (ÉP CHUẨN KIẾN THỨC) ---
def call_ai_pro(word_ru, word_vn):
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key: return "⚠️ Thiếu API Key."
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # PROMPT ÉP AI PHẢI CHUẨN XÁC, KHÔNG ĐƯỢC CHẾ TỪ
    prompt = f"""
    Phân tích từ: '{word_ru}' ({word_vn}).
    YÊU CẦU NGHIÊM NGẶT:
    1. LOẠI TỪ: Xác định rõ là Danh từ, Động từ hay Tính từ.
    2. NẾU LÀ ĐỘNG TỪ: Chia đúng 6 ngôi hiện tại. Chú ý các động từ bất quy tắc (ví dụ: muốn - хотеть -> я хочу, ты хочешь... KHÔNG ĐƯỢC CÓ 'хочую'). Chia quá khứ (4 dạng) và Mệnh lệnh.
    3. NẾU LÀ DANH TỪ: Xác định GIỐNG (Gender) chuẩn xác. Chia 6 cách số ít & số nhiều.
    4. NẾU LÀ TÍNH TỪ: Chia bảng 6 cách.
    5. ĐẶT CÂU: 3 ví dụ tự nhiên nhất, đúng ngữ pháp, dịch Việt chuẩn.
    6. CẤM: Không được đưa ví dụ của từ khác vào bài phân tích. Tô đậm đuôi biến đổi bằng **.
    """
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Bạn là giáo viên tiếng Nga chuyên nghiệp, chính xác tuyệt đối về ngữ pháp. Bạn không bao giờ bịa đặt từ không có thực."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0 # Để độ chính xác là cao nhất
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        return r.json()['choices'][0]['message']['content']
    except: return "⚠️ AI đang bận."

# --- 3. KHỞI TẠO DỮ LIỆU ---
if 'pool' not in st.session_state: st.session_state.pool = []
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'status' not in st.session_state: st.session_state.status = None
if 'ai_res' not in st.session_state: st.session_state.ai_res = ""

# --- 4. THANH BÊN ---
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1513326738677-b964603b136d?q=80&w=400", caption="🇷🇺 Nước Nga")
    f = st.file_uploader("Nạp file .xlsx", type=["xlsx"])
    if f:
        try:
            df = pd.read_excel(f, engine='openpyxl')
            df.columns = [str(c).strip().lower() for c in df.columns]
            if st.button("BẮT ĐẦU HỌC 🚀"):
                st.session_state.pool = df.dropna(how='all').to_dict('records')
                random.shuffle(st.session_state.pool)
                st.session_state.idx = 0
                st.session_state.status, st.session_state.ai_res = None, ""
                st.rerun()
        except Exception as e: st.error(f"Lỗi đọc file: {e}")

# --- 5. GIAO DIỆN CHÍNH ---
st.title("Russian Expert v40.4")

if st.session_state.pool:
    if st.session_state.idx >= len(st.session_state.pool):
        st.success("Hoàn thành!")
        if st.button("Học lại 🔄"):
            st.session_state.idx = 0
            st.rerun()
    else:
        curr = st.session_state.pool[st.session_state.idx]
        c_ru = next((k for k in curr.keys() if any(x in k for x in ['nga', 'ru'])), None)
        c_vn = next((k for k in curr.keys() if any(x in k for x in ['việt', 'vn'])), None)

        if c_ru and c_vn:
            w_ru, w_vn = str(curr[c_ru]).strip(), str(curr[c_vn]).strip()
            st.write(f"🔢 Từ: **{st.session_state.idx + 1}** / **{len(st.session_state.pool)}**")
            st.markdown(f'<div class="ques-box"><div class="ques-vn">{w_vn}</div></div>', unsafe_allow_html=True)

            with st.form(key=f"f4_{st.session_state.idx}"):
                u_in = st.text_input("Đáp án tiếng Nga:", value="")
                btn = st.form_submit_button("KIỂM TRA ✅")

            if btn:
                if u_in.strip().lower() == w_ru.lower():
                    st.session_state.status = 'ok'
                else:
                    st.session_state.status = 'err'
                    st.session_state.pool.insert(st.session_state.idx + 3, curr)
                with st.spinner("Đang phân tích..."):
                    st.session_state.ai_res = call_ai_pro(w_ru, w_vn)

            if st.session_state.status == 'ok': st.success(f"⭐ ĐÚNG: {w_ru}")
            elif st.session_state.status == 'err': st.error(f"❌ SAI! Đáp án: {w_ru}")

            if st.session_state.ai_res:
                with st.expander("📚 KIẾN THỨC CHI TIẾT", expanded=True):
                    st.markdown(st.session_state.ai_res)
                if st.button("Câu tiếp theo ➡️"):
                    st.session_state.idx += 1
                    st.session_state.status, st.session_state.ai_res = None, ""
                    st.rerun()
