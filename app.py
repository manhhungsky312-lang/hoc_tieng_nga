import streamlit as st
import pandas as pd
import requests
import random

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Nga Ngữ Expert v30", layout="centered", page_icon="🇷🇺")

st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    .stApp h1 { color: #1e3a8a; text-align: center; border-bottom: 3px solid #e63946; padding-bottom: 10px; }
    .ques-box {
        background-color: #ffffff; padding: 25px; border-radius: 15px;
        border-left: 10px solid #e63946; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 20px 0;
    }
    .ques-vn { color: #1e293b; font-size: 30px !important; font-weight: 800; text-align: center; }
    table { width: 100%; border-collapse: collapse; margin-top: 15px; background: white; }
    th { background-color: #f1f5f9; color: #1e3a8a; font-weight: bold; padding: 10px; border: 1px solid #cbd5e1; }
    td { border: 1px solid #cbd5e1; padding: 10px; }
    b, strong { color: #dc2626; font-weight: bold; } 
</style>
""", unsafe_allow_html=True)

# --- 2. HÀM GỌI AI TOÀN DIỆN (ĐỘNG TỪ/DANH TỪ/TÍNH TỪ) ---
def call_ai_pro(word_ru, word_vn):
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key: return "⚠️ Thiếu API Key trong Secrets."
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    prompt = f"""
    Phân tích từ: '{word_ru}' ({word_vn}).
    1. NẾU LÀ ĐỘNG TỪ: Chia 6 ngôi hiện tại; Chia quá khứ (đực, cái, trung, nhiều); Mệnh lệnh thức (ты, вы).
    2. NẾU LÀ DANH TỪ: Chia 6 cách số ít & số nhiều (tên cách tiếng Nga); Chuyển sang tính từ tương ứng.
    3. NẾU LÀ TÍNH TỪ: Chia 6 cách; Hiện tính từ ngắn đuôi (краткая форма).
    Lưu ý: Tô đậm đuôi biến đổi bằng **. Tên thành phần bằng tiếng Nga. 3 ví dụ Nga-Việt.
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
    except: return "⚠️ AI đang bận. Hãy thử lại sau giây lát."

# --- 3. KHỞI TẠO BỘ NHỚ BỀN VỮNG ---
if 'pool' not in st.session_state: st.session_state.pool = []
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'status' not in st.session_state: st.session_state.status = None
if 'ai_res' not in st.session_state: st.session_state.ai_res = ""

# --- 4. SIDEBAR: NẠP FILE KHÔNG LỖI ---
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1513326738677-b964603b136d?q=80&w=400", caption="🇷🇺 Nước Nga")
    st.header("📂 Nạp File Excel")
    
    # Nạp file bằng engine thủ công để tránh lỗi thư viện
    uploaded_file = st.file_uploader("Chọn file .xlsx", type=["xlsx"], key="file_loader")
    
    if uploaded_file:
        try:
            # Đọc file với openpyxl để xử lý định dạng mới nhất
            df = pd.read_excel(uploaded_file, engine='openpyxl')
            df.columns = [str(c).strip().lower() for c in df.columns]
            
            # Kiểm tra xem có dữ liệu chưa
            if st.button("KÍCH HOẠT DỮ LIỆU 🚀", key="btn_activate"):
                st.session_state.pool = df.to_dict('records')
                random.shuffle(st.session_state.pool)
                st.session_state.idx = 0
                st.session_state.status = None
                st.session_state.ai_res = ""
                st.success(f"Đã nhận {len(st.session_state.pool)} từ vựng!")
                st.rerun()
        except Exception as e:
            st.error(f"Lỗi file: {e}")

    st.markdown("---")
    st.image("https://images.unsplash.com/photo-1504457047772-27fad17438e2?q=80&w=400", caption="🇻🇳 Việt Nam")

# --- 5. GIAO DIỆN CHÍNH ---
st.title("Russian Expert v30")

if
