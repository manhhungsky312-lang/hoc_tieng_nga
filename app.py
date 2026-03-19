import streamlit as st
import pandas as pd
import requests
import random

# --- 1. TỐI ƯU GIAO DIỆN CHO CẢ PC & MOBILE ---
st.set_page_config(page_title="Nga Ngữ Expert v61", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    .main-card {
        background-color: white; padding: 20px; border-radius: 15px;
        border: 1px solid #e2e8f0; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .word-vn { color: #1e3a8a; font-size: 28px !important; font-weight: 800; text-align: center; }
    /* Font size lớn cho điện thoại */
    @media (max-width: 600px) { .word-vn { font-size: 35px !important; } }
</style>
""", unsafe_allow_html=True)

# --- 2. HÀM AI CHUYÊN SÂU (CHIA CÁCH & THÌ) ---
def call_expert_ai(word_ru, word_vn):
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key: return "⚠️ Thiếu API Key trong Secrets."
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # Lệnh ép AI làm đúng chuyên môn bạn cần
    prompt = f"""
    Phân tích từ: '{word_ru}' ({word_vn}).
    - NẾU DANH TỪ: Giống, chia 6 Cách (Số ít/nhiều), Tính từ liên quan.
    - NẾU ĐỘNG TỪ: Chia 6 ngôi Hiện tại, 4 dạng Quá khứ, Mệnh lệnh, Thể (Hoàn thành/Chưa HT).
    - NẾU TÍNH TỪ: Chia 6 cách.
    - VÍ DỤ: 3 câu Nga-Việt thực tế.
    TRÌNH BÀY: Dùng bảng Markdown, viết đầy đủ từ, không cắt đuôi.
    """
    
    try:
        r = requests.post(url, headers=headers, json={
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "system", "content": "Giáo viên Nga ngữ. Chính xác 100%."},
                         {"role": "user", "content": prompt}],
            "temperature": 0
        }, timeout=25)
        return r.json()['choices'][0]['message']['content']
    except: return "⚠️ Lỗi kết nối AI. Hãy thử lại."

# --- 3. KHỞI TẠO ---
if 'pool' not in st.session_state: st.session_state.pool = []
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'status' not in st.session_state: st.session_state.status = None
if 'ai_res' not in st.session_state: st.session_state.ai_res = ""

# --- 4. XỬ LÝ FILE (FIX LỖI ĐỌC EXCEL) ---
with st.sidebar:
    st.header("📂 Nạp Dữ Liệu")
    f = st.file_uploader("Chọn file .xlsx", type=["xlsx"])
    if f:
        try:
            # Đọc file với engine chuẩn
            df = pd.read_excel(f, engine='openpyxl').dropna(how='all')
            df.columns = [str(c).strip().lower() for c in df.columns]
            
            if st.button("BẮT ĐẦU HỌC 🚀"):
                st.session_state.pool = df.to_dict('records')
                random.shuffle(st.session_state.pool)
                st.session_state.idx = 0
                st.session_state.status, st.session_state.ai_res = None, ""
                st.rerun()
        except Exception as e:
            st.error(f"Lỗi đọc file: {e}. Hãy kiểm tra lại file .xlsx")

# --- 5. GIAO DIỆN CHÍNH ---
st.title("Nga Ngữ Expert v61")

if st.session_state.pool:
    if st.session_state.idx >= len(st.session_state.pool):
        st.success("Hoàn thành!")
        if st.button("Làm lại"): st.session_state.idx = 0; st.rerun()
    else:
        curr = st.session_state.pool[st.session_state.idx]
        # Tìm cột Nga/Việt linh hoạt
        c_ru = next((k for k in curr.keys() if any(x in k for x in ['nga', 'ru'])), None)
        c_vn = next((k for k in curr.keys() if any(x in k for x in ['việt', 'vn'])), None)

        if c_ru and c_vn:
            w_ru, w_vn = str(curr[c_ru]).strip(), str(curr[c_vn]).strip()
            
            st.markdown('<div class="main-card">', unsafe_allow_html=True)
            st.write(f"🔢 {st.session_state.idx + 1} / {len(st.session_state.pool)}")
            st.markdown(f'<div class="word-vn">{w_vn}</div>', unsafe_allow_html=True)

            # Form nhập liệu tối ưu cho mobile
            u_in = st.text_input("Gõ tiếng Nga:", key=f"in_{st.session_state.idx}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("KIỂM TRA ✅"):
                    if u_in.strip().lower() == w_ru.lower():
                        st.session_state.status = 'ok'
                    else:
                        st.session_state.status = 'err'
                        st.session_state.pool.append(curr)
                    with st.spinner("Đang tra ngữ pháp..."):
                        st.session_state.ai_res = call_expert_ai(w_ru, w_vn)
            
            with col2:
                if st.session_state.ai_res:
                    if st.button("TIẾP THEO ➡️"):
                        st.session_state.idx += 1
                        st.session_state.status, st.session_state.ai_res = None, ""
                        st.rerun()

            if st.session_state.status == 'ok': st.success(f"Đúng: {w_ru}")
            elif st.session_state.status == 'err': st.error(f"Sai! Đáp án: {w_ru}")

            if st.session_state.ai_res:
                st.markdown("### 📚 Ngữ pháp & Ví dụ")
                st.markdown(st.session_state.ai_res)
            st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("Hãy nạp file Excel ở thanh bên.")
