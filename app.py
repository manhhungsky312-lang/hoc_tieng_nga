import streamlit as st
import pandas as pd
import requests
import json

# --- 1. CẤU HÌNH HỆ THỐNG ---
st.set_page_config(page_title="Học Tiếng Nga Quân Sự - Gemini v6", layout="centered")

# Lấy API KEY từ Secrets (Bạn nhớ đặt tên là GEMINI_API_KEY trong Streamlit Cloud)
api_key = st.secrets.get("GEMINI_API_KEY")

def call_gemini_analysis(word_ru, word_vn):
    """Gọi trực tiếp Gemini API với cấu hình chính xác tuyệt đối"""
    if not api_key: return "Thiếu API Key trong cấu hình Secrets."
    
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    # Prompt cực kỳ khắt khe để AI không nói sai giống danh từ
    prompt = f"""
    Bạn là một giảng viên tiếng Nga tại Học viện Kỹ thuật Quân sự. 
    Hãy phân tích từ: '{word_ru}' (nghĩa: {word_vn}).
    Yêu cầu trình bày chính xác 100% bằng tiếng Việt:
    1. LOẠI TỪ: (Danh từ/Động từ/Tính từ...).
    2. GIỐNG (Nếu là danh từ): Phải xác định đúng giống Đực/Cái/Trung dựa trên đuôi từ số ít (-а/-я là CÁI; phụ âm là ĐỰC; -о/-е là TRUNG).
    3. BIẾN CÁCH: Chia số ít và số nhiều (Cách 1).
    4. ĐỘNG TỪ: Chia đủ 6 ngôi ở thời hiện tại: я, ты, он/она, мы, вы, они.
    5. VÍ DỤ: 1 câu đời thường + 1 câu QUÂN SỰ thực tế. (Tiếng Nga có dịch tiếng Việt).
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1} # Giảm sáng tạo để tăng độ chính xác
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Lỗi từ máy chủ Google: {response.status_code}"
    except: return "Lỗi kết nối mạng."

# --- 2. KHÓA TRẠNG THÁI (NGĂN NHẢY CÂU) ---
if 'vocab_data' not in st.session_state: st.session_state.vocab_data = None
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'submitted' not in st.session_state: st.session_state.submitted = False

# --- 3. SIDEBAR: NẠP FILE ---
with st.sidebar:
    st.header("📂 Dữ liệu học tập")
    uploaded_file = st.file_uploader("Nạp file Excel (.xlsx)", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        df.columns = [str(c).strip().lower() for c in df.columns]
        # Xáo trộn duy nhất 1 lần khi nạp file và lưu cố định vào session_state
        if st.session_state.vocab_data is None:
            st.session_state.vocab_data = df.sample(frac=1).reset_index(drop=True)
            st.session_state.idx = 0
            st.session_state.submitted = False
            st.success("Đã nạp và xáo trộn xong!")

# --- 4. GIAO DIỆN CHÍNH ---
st.title("🇷🇺 Russian Military Learning")

if st.session_state.vocab_data is not None:
    data = st.session_state.vocab_data
    c_ru = next((c for c in data.columns if any(k in c for k in ['nga', 'ru'])), None)
    c_vn = next((c for c in data.columns if any(k in c for k in ['việt', 'vn', 'viet'])), None)

    if c_ru and c_vn:
        # Lấy từ vựng cố định theo chỉ số hiện tại
        current_row = data.iloc[st.session_state.idx]
        word_ru_correct = str(current_row[c_ru]).strip()
        word_vn_display = str(current_row[c_vn]).strip()

        st.info(f"Từ số {st.session_state.idx + 1} / {len(data)}")
        st.markdown(f"### Dịch sang tiếng Nga: <span style='color:red'>{word_vn_display}</span>", unsafe_allow_html=True)

        # FORM ĐỂ KHÓA DỮ LIỆU: Bấm nút bên trong Form sẽ không làm nhảy sang từ khác
        with st.form(key=f"form_word_{st.session_state.idx}"):
            user_input = st.text_input("Nhập đáp án tiếng Nga:", value="")
            btn_check = st.form_submit_button("KIỂM TRA ✅")

        if btn_check:
            st.session_state.submitted = True
            if user_input.strip().lower() == word_ru_correct.lower():
                st.success(f"⭐ CHÍNH XÁC! Đáp án: {word_ru_correct}")
            else:
                st.error(f"❌ SAI RỒI! Đáp án đúng: {word_ru_correct}")

            with st.spinner("Gemini đang phân tích ngữ pháp quân sự..."):
                analysis = call_gemini_analysis(word_ru_correct, word_vn_display)
                st.markdown("---")
                st.info(analysis)

        # Nút chuyển câu chỉ hiện ra sau khi đã trả lời xong
        if st.session_state.submitted:
            if st.button("Từ tiếp theo ➡️"):
                if st.session_state.idx < len(data) - 1:
                    st.session_state.idx += 1
                else:
                    st.session_state.idx = 0
                st.session_state.submitted = False
                st.rerun()
    else:
        st.error("File Excel cần có cột 'Tiếng Nga' và 'Tiếng Việt'.")
else:
    st.write("Hãy nạp file Excel ở thanh bên trái để bắt đầu bài học.")
