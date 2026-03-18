import streamlit as st
import pandas as pd
import requests
import random

# --- 1. CẤU HÌNH GIAO DIỆN CHUYÊN NGHIỆP ---
st.set_page_config(page_title="Nga Ngữ Expert v29", layout="centered", page_icon="🇷🇺")

st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    .stApp h1 { color: #1e3a8a; text-align: center; border-bottom: 3px solid #e63946; padding-bottom: 10px; }
    .ques-box {
        background-color: #ffffff; padding: 30px; border-radius: 15px;
        border-left: 10px solid #e63946; box-shadow: 0 10px 15px rgba(0,0,0,0.1); margin: 20px 0;
    }
    .ques-vn { color: #1e293b; font-size: 30px !important; font-weight: 800; text-align: center; }
    table { width: 100%; border-collapse: collapse; margin-top: 15px; background: white; }
    th { background-color: #f1f5f9; color: #1e3a8a; font-weight: bold; text-align: center !important; padding: 10px; border: 1px solid #cbd5e1; }
    td { border: 1px solid #cbd5e1; padding: 10px; text-align: left; }
    b, strong { color: #dc2626; font-weight: bold; } /* Đuôi biến đổi màu đỏ */
</style>
""", unsafe_allow_html=True)

api_key = st.secrets.get("GROQ_API_KEY")

def call_ai_comprehensive(word_ru, word_vn):
    if not api_key: return "⚠️ Thiếu API Key trong Secrets."
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # PROMPT HỆ THỐNG: XỬ LÝ ĐA DẠNG LOẠI TỪ
    prompt = f"""
    Phân tích từ tiếng Nga: '{word_ru}' ({word_vn}).
    
    YÊU CẦU THEO LOẠI TỪ:
    1. NẾU LÀ ĐỘNG TỪ (Глагол):
       - Chia 6 ngôi HIỆN TẠI (hoặc Tương lai đơn).
       - Chia QUÁ KHỨ (Прошедшее время): Giống đực, Giống cái, Giống trung, Số nhiều.
       - MỆNH LỆNH THỨC (Повелительное наклонение): Ngôi 'Ты' và 'Вы'.
       
    2. NẾU LÀ DANH TỪ (Существительное):
       - Bảng 6 CÁCH (Именительный...): Số ít và Số nhiều.
       - Chuyển đổi sang TÍNH TỪ tương ứng (Прилагательное).
       
    3. NẾU LÀ TÍNH TỪ (Прилагательное):
       - Bảng 6 CÁCH (Giống đực, cái, trung, số nhiều).
       - TÍNH TỪ NGẮN ĐUÔI (Краткая форма): Đực, Cái, Trung, Nhiều.

    LƯU Ý CHUNG: 
    - Tên các thành phần ngữ pháp bằng TIẾNG NGA.
    - TÔ ĐẬM phần đuôi biến đổi bằng **.
    - 3 ví dụ thực tế Nga-Việt.
    """
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Bạn là chuyên gia ngôn ngữ Nga. Phân tích sâu, chính xác các hình thái từ. Chỉ khẳng định đúng, không rườm rà."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=20)
        return response.json()['choices'][0]['message']['content']
    except: return "⚠️ AI đang bận xử lý dữ liệu phức tạp."

# --- 2. LOGIC BỘ NHỚ ---
if 'pool' not in st.session_state: st.session_state.pool = [] 
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'status' not in st.session_state: st.session_state.status = None 
if 'ai_res' not in st.session_state: st.session_state.ai_res = ""

# --- 3. SIDEBAR ---
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1513326738677-b964603b136d?q=80&w=400", caption="🇷🇺 Nước Nga")
    file = st.file_uploader("Nạp file Excel vựng", type=["xlsx"])
    if file and not st.session_state.pool:
        df = pd.read_excel(file)
        df.columns = [str(c).strip().lower() for c in df.columns]
        st.session_state.pool = df.to_dict('records')
        random.shuffle(st.session_state.pool)
        st.success("Đã nạp file thành công!")
        st.rerun()
    st.image("https://images.unsplash.com/photo-1504457047772-27fad17438e2?q=80&w=400", caption="🇻🇳 Việt Nam")

# --- 4. GIAO DIỆN CHÍNH ---
st.title("Russian Expert v29")

if st.session_state.pool:
    curr = st.session_state.pool[st.session_state.idx]
    c_ru = next((k for k in curr.keys() if 'nga' in k or 'ru' in k), None)
    c_vn = next((k for k in curr.keys() if 'việt' in k or 'vn' in k), None)

    if c_ru and c_vn:
        w_ru, w_vn = str(curr[c_ru]).strip(), str(curr[c_vn]).strip()
        
        st.markdown(f'<div class="ques-box"><div style="font-size:16px; color:#64748b; font-weight:bold;">DỊCH SANG TIẾNG NGA:</div><div class="ques-vn">{w_vn}</div></div>', unsafe_allow_html=True)

        with st.form(key=f"v29_f_{st.session_state.idx}"):
            u_in = st.text_input("Đáp án của bạn:", value="")
            sub = st.form_submit_button("KIỂM TRA & PHÂN TÍCH CHUYÊN SÂU ✅")

        if sub:
            if u_in.strip().lower() == w_ru.lower():
                st.session_state.status = 'ok'
                st.success(f"⭐ CHÍNH XÁC: {w_ru}")
                with st.spinner("AI đang trích xuất toàn bộ hình thái từ..."):
                    st.session_state.ai_res = call_ai_comprehensive(w_ru, w_vn)
            else:
                st.session_state.status = 'err'
                st.error(f"❌ SAI! Đáp án đúng: {w_ru}")
                st.session_state.pool.append(curr)

        if st.session_state.status == 'ok' and st
