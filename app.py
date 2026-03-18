import streamlit as st
import pandas as pd
import requests
import random

# --- 1. CẤU HÌNH GIAO DIỆN (PHỤC HỒI HÌNH ẢNH & CSS) ---
st.set_page_config(page_title="Nga Ngữ Expert v31.6", layout="centered", page_icon="🇷🇺")

st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    .stApp h1 { color: #1e3a8a; text-align: center; border-bottom: 3px solid #e63946; padding-bottom: 10px; }
    .ques-box {
        background-color: #ffffff; padding: 25px; border-radius: 15px;
        border-left: 10px solid #e63946; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 20px 0;
    }
    .ques-vn { color: #1e293b; font-size: 30px !important; font-weight: 800; text-align: center; }
    b, strong { color: #dc2626; font-weight: bold; } 
    table { width: 100%; border-collapse: collapse; margin-top: 15px; background: white; }
    th { background-color: #f1f5f9; padding: 10px; border: 1px solid #cbd5e1; color: #1e3a8a; }
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

# --- 3. HÀM GỌI AI (KHÓA LOGIC GIỐNG & ĐẶT CÂU) ---
def call_ai_pro(word_ru, word_vn):
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key: return "⚠️ Thiếu API Key trong Secrets."
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    prompt = f"""
    Phân tích từ: '{word_ru}' ({word_vn}).
    
    YÊU CẦU NGHIÊM NGẶT:
    1. XÁC ĐỊNH GIỐNG (GENDER): Bạn phải xác định đúng. Ví dụ 'Песня' kết thúc bằng -я là Giống cái (Женский род). 'Море' kết thúc bằng -е là Giống trung (Средний род).
    2. DANH TỪ: Chia 6 cách số ít & số nhiều (Sử dụng tên: Danh cách, Sinh cách, Tặng cách, Đối cách, Cách công cụ, Cách giới từ). Chuyển sang tính từ tương ứng.
    3. ĐỘNG TỪ: Chia 6 ngôi hiện tại; Quá khứ (đực, cái, trung, nhiều); Mệnh lệnh (ты, вы).
    4. TÍNH TỪ: Chia bảng 6 cách; Tính từ ngắn đuôi (Краткая форма).
    5. ĐẶT CÂU: Cung cấp 3 ví dụ đặt câu tự nhiên nhất (Nga - Việt).
    
    Lưu ý: Tô đậm đuôi biến đổi bằng **. Tên thành phần bằng tiếng Nga.
    """
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Bạn là giáo viên tiếng Nga chuyên nghiệp. Bạn tuyệt đối không nhầm lẫn giống của danh từ. Bạn đặt câu giao tiếp đời thường tự nhiên."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        return r.json()['choices'][0]['message']['content']
    except: return "⚠️ AI đang bận."

# --- 4. KHỞI TẠO SESSION STATE ---
if 'pool' not in st.session_state: st.session_state.pool = []
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'status' not in st.session_state: st.session_state.status = None
if 'ai_res' not in st.session_state: st.session_state.ai_res = ""

# --- 5. SIDEBAR (CÓ HÌNH ẢNH) ---
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1513326738677-b964603b136d?q=80&w=400", caption="🇷🇺 Nước Nga")
    st.header("📂 Nạp Dữ Liệu")
    f = st.file_uploader("Chọn file .xlsx", type=["xlsx"])
    
    if f:
        data = load_data(f)
        if isinstance(data, str):
            st.error(f"Lỗi: {data}")
        else:
            if st.button("BẮT ĐẦU HỌC 🚀"):
                st.session_state.pool = data.copy()
                random.shuffle(st.session_state.pool)
                st.session_state.idx = 0
                st.session_state.status = None
                st.session_state.ai_res = ""
                st.rerun()
    st.markdown("---")
    st.image("https://images.unsplash.com/photo-1504457047772-27fad17438e2?q=80&w=400", caption="🇻🇳 Việt Nam")

# --- 6. GIAO DIỆN CHÍNH ---
st.title("Russian Expert v31.6")

if st.session
