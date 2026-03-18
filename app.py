import streamlit as st
import pandas as pd
import requests
import random

# --- 1. CẤU HÌNH ---
st.set_page_config(page_title="Học Tiếng Nga Quân Sự v2", layout="wide")

api_key = st.secrets.get("GROQ_API_KEY")

def call_ai_analysis(word_ru, word_vn):
    if not api_key: return "Chưa cấu hình API Key."
    
    # PROMPT ÉP AI CHUẨN XÁC TUYỆT ĐỐI VỀ GIỐNG VÀ CÁCH CHIA
    prompt = f"""
    Hãy phân tích từ tiếng Nga: '{word_ru}' (nghĩa: {word_vn}).
    Yêu cầu trình bày theo cấu trúc học thuật:
    1. Loại từ và Giống (Danh từ giống Đực/Cái/Trung). PHẢI XÁC ĐỊNH ĐÚNG ĐUÔI TỪ.
    2. Nếu là Danh từ: Chia số ít và số nhiều (Cách 1).
    3. Nếu là Động từ: Cho biết cặp khía cạnh (Hoàn thành/Chưa hoàn thành). Chia ở thời HIỆN TẠI (hoặc TƯƠNG LAI đơn) theo 6 ngôi: я, ты, он/она, мы, вы, они.
    4. Đặt 2 câu ví dụ (Tiếng Nga có dịch tiếng Việt):
       - 1 câu đời thường.
       - 1 câu chuyên ngành QUÂN SỰ hoặc KỸ THUẬT (Sử dụng từ vựng chuyên môn thực tế).
    Ghi chú: Trả lời bằng tiếng Việt, súc tích, chính xác.
    """
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Bạn là giáo sư tiếng Nga tại học viện quân sự. Trả lời cực kỳ chính xác về ngữ pháp, không nhầm lẫn giống của danh từ."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0 # Ép AI trả lời máy móc theo quy tắc, không sáng tạo linh tinh
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.json()['choices'][0]['message']['content']
    except: return "Lỗi hệ thống AI."

# --- 2. QUẢN LÝ TRẠNG THÁI ---
if 'data' not in st.session_state: st.session_state.data = None
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'submitted' not in st.session_state: st.session_state.submitted = False

# --- 3. SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Dữ liệu")
    uploaded_file = st.file_uploader("Nạp file Excel", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        df.columns = [str(c).strip().lower() for c in df.columns]
        # Xáo trộn 1 lần duy nhất
        st.session_state.data = df.sample(frac=1).reset_index(drop=True)
        st.session_state.idx = 0
        st.session_state.submitted = False
        st.success("Đã nạp và xáo trộn từ vựng!")

# --- 4. GIAO DIỆN CHÍNH ---
st.title("🇷🇺 Russian Military Training Center")

if st.session_state.data is not None:
    df = st.session_state.data
    col_ru = next((c for c in df.columns if any(k in c for k in ['nga', 'ru'])), None)
    col_vn = next((c for c in df.columns if any(k in c for k in ['việt', 'vn', 'viet'])), None)

    if col_ru and col_vn:
        row = df.iloc[st.session_state.idx]
        word_ru = str(row[col_ru]).strip()
        word_vn = str(row[col_vn]).strip()

        st.info(f"Từ số: {st.session_state.idx + 1} / {len(df)}")
        st.markdown(f"### Dịch sang tiếng Nga: <span style='color:blue'>{word_vn}</span>", unsafe_allow_html=True)

        # Form nhập liệu
        with st.form(key=f"form_{st.session_state.idx}"):
            user_input = st.text_input("Nhập đáp án tiếng Nga:", value="")
            btn_check = st.form_submit_button("Kiểm tra ✅")

        if btn_check:
            st.session_state.submitted = True
            if user_input.strip().lower() == word_ru.lower():
                st.success(f"⭐ CHÍNH XÁC! Đáp án: **{word_ru}**")
            else:
                st.error(f"❌ SAI RỒI! Đáp án đúng là: **{word_ru}**")
                st.warning(f"Gợi ý: Hãy chú ý đuôi từ để xác định giống của '{word_ru}'.")

            with st.spinner("🤖 AI đang phân tích ngữ pháp quân sự..."):
                analysis = call_ai_analysis(word_ru, word_vn)
                st.markdown("---")
                st.markdown(analysis)

        # Nút nhảy câu chỉ xuất hiện sau khi đã trả lời
        if st.session_state.submitted:
            if st.button("Từ tiếp theo ➡️"):
                if st.session_state.idx < len(df) - 1:
                    st.session_state.idx += 1
                else:
                    st.session_state.idx = 0
                st.session_state.submitted = False
                st.rerun()
    else:
        st.error("File Excel thiếu cột Tiếng Nga hoặc Tiếng Việt.")
else:
    st.write("Mời bạn nạp file Excel ở Menu bên trái để bắt đầu huấn luyện.")
