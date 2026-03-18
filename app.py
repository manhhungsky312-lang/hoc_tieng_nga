import streamlit as st
import pandas as pd
import requests
import random
import io

# 1. CẤU HÌNH GIAO DIỆN
st.set_page_config(page_title="Nga Ngữ Expert v28", layout="centered", page_icon="🇷🇺")

st.markdown("""
<style>
    .stApp h1 { color: #1e3a8a; text-align: center; border-bottom: 3px solid #e63946; }
    .ques-vn { 
        font-size: 32px !important; font-weight: 800; color: #1e293b; text-align: center; 
        padding: 25px; background-color: #ffffff; border-radius: 15px; 
        border-left: 10px solid #e63946; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 25px; 
    }
    b, strong { color: #dc2626; font-weight: bold; } 
    table { width: 100%; border-collapse: collapse; }
    th { background-color: #f1f5f9; padding: 10px; border: 1px solid #cbd5e1; color: #1e3a8a; }
    td { border: 1px solid #cbd5e1; padding: 10px; }
</style>
""", unsafe_allow_html=True)

# 2. HÀM AI (THÔNG MINH PHÂN BIỆT LOẠI TỪ)
def call_ai_smart(word_ru, word_vn):
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key: return "⚠️ Thiếu API Key trong Secrets."
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    prompt = f"Phân tích từ: '{word_ru}' ({word_vn}). 1. Xác định loại từ (Động từ hay Danh từ). 2. Nếu Động từ: chia 6 ngôi Hiện tại. Nếu Danh từ: chia 6 Cách (tên cách tiếng Nga) số ít & số nhiều. 3. Tô đậm đuôi biến đổi bằng **. 4. 3 ví dụ Nga-Việt."
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": "Chuyên gia Nga ngữ. Phân biệt Verb/Noun. Không chia Cách cho Động từ."},
                     {"role": "user", "content": prompt}],
        "temperature": 0.1
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=15)
        return r.json()['choices'][0]['message']['content']
    except: return "⚠️ AI bận."

# 3. KHỞI TẠO SESSION STATE
if 'pool' not in st.session_state: st.session_state.pool = []
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'status' not in st.session_state: st.session_state.status = None
if 'ai_response' not in st.session_state: st.session_state.ai_response = ""

# 4. SIDEBAR (NẠP FILE CƯỜNG LỰC)
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1513326738677-b964603b136d?q=80&w=400", caption="🇷🇺 Nước Nga")
    st.header("📂 Nạp Dữ Liệu")
    
    file = st.file_uploader("Chọn file Excel (.xlsx)", type=["xlsx"])
    
    if file:
        try:
            # Đọc file dùng engine openpyxl để tránh lỗi định dạng
            df = pd.read_excel(file, engine='openpyxl')
            df.columns = [str(c).strip().lower() for c in df.columns]
            
            st.write("✅ Đã đọc được file!")
            st.dataframe(df.head(3)) # Hiện 3 dòng đầu để bạn kiểm tra
            
            if st.button("BẮT ĐẦU HỌC NGAY 🚀"):
                st.session_state.pool = df.to_dict('records')
                random.shuffle(st.session_state.pool)
                st.session_state.idx = 0
                st.session_state.status = None
                st.session_state.ai_response = ""
                st.rerun()
        except Exception as e:
            st.error(f"Lỗi đọc file: {e}. Hãy đảm bảo file không bị đặt mật khẩu.")

    st.markdown("---")
    st.image("https://images.unsplash.com/photo-1504457047772-27fad17438e2?q=80&w=400", caption="🇻🇳 Việt Nam")

# 5. GIAO DIỆN CHÍNH
st.title("Russian Expert v28")

if st.session_state.pool:
    item = st.session_state.pool[st.session_state.idx]
    c_ru = next((k for k in item.keys() if 'nga' in k or 'ru' in k), None)
    c_vn = next((k for k in item.keys() if 'việt' in k or 'vn' in k), None)

    if c_ru and c_vn:
        w_ru, w_vn = str(item[c_ru]).strip(), str(item[c_vn]).strip()
        st.write(f"🔢 Câu hỏi số: **{st.session_state.idx + 1}** / **{len(st.session_state.pool)}**")
        st.markdown(f'<div class="ques-vn"><div style="font-size:14px; color:#64748b; margin-bottom:5px;">DỊCH SANG TIẾNG NGA:</div>{w_vn}</div>', unsafe_allow_html=True)

        with st.form(key=f"f_{st.session_state.idx}"):
            u_in = st.text_input("Đáp án:", value="", placeholder="Nhập từ...")
            sub = st.form_submit_button("KIỂM TRA ✅")

        if sub:
            if u_in.strip().lower() == w_ru.lower():
                st.session_state.status, st.session_state.ai_response = 'correct', call_ai_smart(w_ru, w_vn)
                st.success(f"⭐ ĐÚNG! Đáp án: {w_ru}")
            else:
                st.session_state.status = 'wrong'
                st.error(f"❌ SAI! Đáp án đúng: {w_ru}")
                st.session_state.pool.append(item)

        if st.session_state.status == 'correct' and st.session_state.ai_response:
            with st.expander("📚 BÀI HỌC CHI TIẾT", expanded=True):
                st.markdown(st.session_state.ai_response)

        if st.session_state.status:
            if st.button("Từ tiếp theo ➡️"):
                st.session_state.pool.pop(st.session_state.idx)
                if not st.session_state.pool: st.balloons()
                elif st.session_state.idx >= len(st.session_state.pool): st.session_state.idx = 0
                st.session_state.status, st.session_state.ai_response = None, ""
                st.rerun()
    else: st.error("File Excel thiếu cột 'Nga' và 'Việt'.")
else: st.info("Mời nạp file Excel ở thanh bên để bắt đầu.")
