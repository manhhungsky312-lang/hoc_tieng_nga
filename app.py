import streamlit as st
import pandas as pd
import requests
import random

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Nga Ngữ Expert v40.5", layout="centered", page_icon="🇷🇺")

st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    .ques-box {
        background-color: #ffffff; padding: 25px; border-radius: 15px;
        border-left: 10px solid #e63946; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 20px 0;
    }
    .ques-vn { color: #1e293b; font-size: 32px !important; font-weight: 800; text-align: center; }
    b, strong { color: #dc2626; font-weight: bold; } 
    table { width: 100%; border-collapse: collapse; margin: 15px 0; background: white; }
    th { background-color: #f1f5f9; padding: 10px; border: 1px solid #cbd5e1; color: #1e3a8a; font-weight: bold; }
    td { border: 1px solid #cbd5e1; padding: 10px; text-align: left; }
</style>
""", unsafe_allow_html=True)

# --- 2. HÀM GỌI AI (ÉP VIẾT ĐẦY ĐỦ TỪ - KHÔNG CẮT CỤT) ---
def call_ai_pro(word_ru, word_vn):
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key: return "⚠️ Thiếu API Key trong Secrets."
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # PROMPT MỚI: ÉP AI PHẢI VIẾT NGUYÊN CẢ TỪ ĐÃ CHIA
    prompt = f"""
    Phân tích từ: '{word_ru}' ({word_vn}).
    
    YÊU CẦU TỐI THƯỢNG:
    1. KHÔNG ĐƯỢC chỉ viết mỗi đuôi từ. Phải viết ĐẦY ĐỦ NGUYÊN TỪ đã chia (Ví dụ: Я смеюсь, không được viết Я ю).
    2. ĐỘNG TỪ: Chia đúng 6 ngôi hiện tại, quá khứ (4 dạng), mệnh lệnh (ты, вы). Chú ý động từ phản thân đuôi -ся/-сь. 
    3. DANH TỪ: Xác định GIỐNG chính xác. Chia đầy đủ 6 cách (Số ít & Số nhiều) kèm ví dụ cụ thể cho từng cách.
    4. ĐẶT CÂU: 3 ví dụ tự nhiên nhất, không máy móc.
    5. TRÌNH BÀY: Sử dụng BẢNG Markdown cho phần chia cách và chia động từ để dễ nhìn.
    
    Tô đậm phần đuôi biến đổi bằng dấu ** (Ví dụ: сме**юсь**).
    """
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Bạn là giáo viên tiếng Nga chuyên nghiệp. Bạn phải viết đầy đủ từ, không bao giờ để trống gốc từ. Bạn xác định giống danh từ cực kỳ chính xác."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=25)
        return r.json()['choices'][0]['message']['content']
    except: return "⚠️ Máy chủ AI đang bận, vui lòng thử lại."

# --- 3. KHỞI TẠO SESSION STATE ---
for key in ['pool', 'idx', 'status', 'ai_res']:
    if key not in st.session_state:
        if key == 'pool': st.session_state[key] = []
        elif key == 'idx': st.session_state[key] = 0
        elif key == 'ai_res': st.session_state[key] = ""
        else: st.session_state[key] = None

# --- 4. SIDEBAR ---
with st.sidebar:
    st.header("📂 Dữ Liệu")
    f = st.file_uploader("Nạp file .xlsx", type=["xlsx"])
    if f:
        try:
            df = pd.read_excel(f, engine='openpyxl').dropna(how='all')
            df.columns = [str(c).strip().lower() for c in df.columns]
            if st.button("BẮT ĐẦU HỌC 🚀"):
                st.session_state.pool = df.to_dict('records')
                random.shuffle(st.session_state.pool)
                st.session_state.idx, st.session_state.status, st.session_state.ai_res = 0, None, ""
                st.rerun()
        except Exception as e: st.error(f"Lỗi: {e}")

# --- 5. GIAO DIỆN CHÍNH ---
st.title("Russian Expert v40.5")

if st.session_state.pool:
    if st.session_state.idx >= len(st.session_state.pool):
        st.success("Hoàn thành bài học!")
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

            with st.form(key=f"f5_{st.session_state.idx}"):
                u_in = st.text_input("Đáp án tiếng Nga:", value="", placeholder="Gõ từ...")
                btn = st.form_submit_button("KIỂM TRA ✅")

            if btn:
                if u_in.strip().lower() == w_ru.lower():
                    st.session_state.status = 'ok'
                else:
                    st.session_state.status = 'err'
                    st.session_state.pool.insert(st.session_state.idx + 3, curr)
                with st.spinner("Đang tra cứu ngữ pháp chuẩn..."):
                    st.session_state.ai_res = call_ai_pro(w_ru, w_vn)

            if st.session_state.status == 'ok': st.success(f"⭐ CHÍNH XÁC!")
            elif st.session_state.status == 'err': st.error(f"❌ SAI! Đáp án đúng: {w_ru}")

            if st.session_state.ai_res:
                with st.expander("📚 BÀI HỌC CHI TIẾT", expanded=True):
                    st.markdown(st.session_state.ai_res)
                if st.button("Từ tiếp theo ➡️"):
                    st.session_state.idx += 1
                    st.session_state.status, st.session_state.ai_res = None, ""
                    st.rerun()
else: st.info("Mời nạp file Excel.")
