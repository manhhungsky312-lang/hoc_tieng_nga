import streamlit as st
import pandas as pd
import requests
import random

# --- 1. GIAO DIỆN CHUYÊN NGHIỆP ---
st.set_page_config(page_title="Nga Ngữ Expert v60", layout="wide", page_icon="🇷🇺")

st.markdown("""
<style>
    .stApp { background-color: #f1f5f9; }
    .main-card {
        background-color: white; padding: 30px; border-radius: 20px;
        border-top: 8px solid #1e3a8a; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }
    .word-vn { color: #1e3a8a; font-size: 40px !important; font-weight: 800; text-align: center; margin-bottom: 20px; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; }
    table { width: 100%; border-collapse: collapse; background: #ffffff; }
    th { background-color: #1e3a8a; color: white; padding: 12px; border: 1px solid #dee2e6; }
    td { border: 1px solid #dee2e6; padding: 12px; text-align: left; font-size: 16px; }
    .correct { color: #15803d; font-weight: bold; font-size: 20px; }
    .error { color: #b91c1c; font-weight: bold; font-size: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 2. HÀM AI "BẢN ĐỒ NGỮ PHÁP" ---
def call_expert_ai(word_ru, word_vn):
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key: return "⚠️ Lỗi: Chưa nạp API Key."
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # PROMPT "THIẾT QUÂN LUẬT" - ÉP AI KHÔNG ĐƯỢC LÀM SAI
    prompt = f"""
    Bạn là Giáo sư ngôn ngữ học Nga-Việt. Phân tích từ: '{word_ru}' ({word_vn}).
    
    YÊU CẦU BẮT BUỘC:
    1. XÁC ĐỊNH LOẠI TỪ: Danh từ, Động từ hay Tính từ.
    2. NẾU LÀ DANH TỪ: 
       - Giống (Đực/Cái/Trung).
       - Bảng chia 6 Cách (Số ít & Số nhiều). 
       - Tìm Tính từ liên quan (Ví dụ: phố -> thuộc về phố).
    3. NẾU LÀ ĐỘNG TỪ:
       - Thể (Hoàn thành/Chưa hoàn thành).
       - Chia 6 ngôi Hiện tại (hoặc Tương lai đơn).
       - Chia 4 dạng Quá khứ (Nam, Nữ, Trung, Nhiều).
       - Mệnh lệnh thức (ты, вы).
    4. NẾU LÀ TÍNH TỪ: Chia 6 cách theo Giống Đực.
    5. VÍ DỤ: 3 câu thực tế, dịch Việt chuẩn.
    
    TRÌNH BÀY: Dùng bảng Markdown rõ ràng. Đánh dấu trọng âm bằng dấu gạch hoặc viết hoa chữ cái có trọng âm.
    """
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Bạn là giáo viên Nga ngữ chính xác tuyệt đối. Bạn không bao giờ bịa từ. Bạn nắm vững mọi ngoại lệ ngữ pháp."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=25)
        return r.json()['choices'][0]['message']['content']
    except: return "⚠️ AI đang bận xử lý dữ liệu phức tạp."

# --- 3. QUẢN LÝ TRẠNG THÁI ---
if 'pool' not in st.session_state: st.session_state.pool = []
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'ans_state' not in st.session_state: st.session_state.ans_state = None # None, 'correct', 'wrong'
if 'ai_cache' not in st.session_state: st.session_state.ai_cache = ""

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Cấu hình")
    f = st.file_uploader("Nạp danh sách từ (.xlsx)", type=["xlsx"])
    if f:
        try:
            df = pd.read_excel(f, engine='openpyxl').dropna(how='all')
            df.columns = [str(c).strip().lower() for c in df.columns]
            if st.button("🚀 BẮT ĐẦU HỌC NGAY"):
                st.session_state.pool = df.to_dict('records')
                random.shuffle(st.session_state.pool)
                st.session_state.idx = 0
                st.session_state.ans_state = None
                st.session_state.ai_cache = ""
                st.rerun()
        except: st.error("Lỗi đọc file Excel!")

# --- 5. KHÔNG GIAN HỌC TẬP ---
if st.session_state.pool:
    if st.session_state.idx >= len(st.session_state.pool):
        st.balloons()
        st.success("BÁO CÁO: Bạn đã hoàn thành toàn bộ nội dung học tập!")
        if st.button("Học lại từ đầu 🔄"):
            st.session_state.idx = 0; st.rerun()
    else:
        curr = st.session_state.pool[st.session_state.idx]
        # Tìm cột thông minh
        c_ru = next((k for k in curr.keys() if any(x in k for x in ['nga', 'ru'])), None)
        c_vn = next((k for k in curr.keys() if any(x in k for x in ['việt', 'vn'])), None)
        
        if c_ru and c_vn:
            w_ru, w_vn = str(curr[c_ru]).strip(), str(curr[c_vn]).strip()
            
            st.markdown(f'<div class="main-card">', unsafe_allow_html=True)
            st.write(f"📊 Tiến độ: {st.session_state.idx + 1} / {len(st.session_state.pool)}")
            st.markdown(f'<div class="word-vn">{w_vn}</div>', unsafe_allow_html=True)
            
            with st.form(key=f"study_form_{st.session_state.idx}"):
                u_in = st.text_input("Gõ đáp án tiếng Nga (kiểm tra khả năng nhớ từ):", value="")
                submit = st.form_submit_button("KIỂM TRA & XEM NGỮ PHÁP ✅")
            
            if submit:
                if u_in.strip().lower() == w_ru.lower():
                    st.session_state.ans_state = 'correct'
                else:
                    st.session_state.ans_state = 'wrong'
                    # Nhét vào cuối để học lại cho đến khi thuộc
                    st.session_state.pool.append(curr)
                
                with st.spinner("Đang truy xuất bảng chia cách và thì động từ..."):
                    st.session_state.ai_cache = call_expert_ai(w_ru, w_vn)

            if st.session_state.ans_state == 'correct':
                st.markdown(f'<p class="correct">⭐ CHÍNH XÁC: {w_ru}</p>', unsafe_allow_html=True)
            elif st.session_state.ans_state == 'wrong':
                st.markdown(f'<p class="error">❌ SAI! Đáp án đúng: {w_ru}</p>', unsafe_allow_html=True)

            if st.session_state.ai_cache:
                st.markdown("### 📚 CHI TIẾT NGỮ PHÁP")
                st.markdown(st.session_state.ai_cache)
                
                if st.button("Từ tiếp theo ➡️"):
                    st.session_state.idx += 1
                    st.session_state.ans_state = None
                    st.session_state.ai_cache = ""
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else: st.error("Lỗi: File thiếu cột Nga/Việt.")
else:
    st.info("Hãy nạp file Excel ở thanh bên để bắt đầu chương trình học chuyên sâu.")
