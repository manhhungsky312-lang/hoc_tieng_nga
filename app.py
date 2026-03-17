import streamlit as st
import pandas as pd
import requests
import random

# --- 1. CẤU HÌNH ---
st.set_page_config(page_title="Học Tiếng Nga Chuyên Sâu", layout="centered")

# Lấy API KEY của Groq
api_key = st.secrets.get("GROQ_API_KEY")

def call_ai_analysis(word_ru, word_vn):
    """Gọi AI phân tích chi tiết ngữ pháp và đặt câu chuyên sâu"""
    if not api_key:
        return "Lỗi: Chưa cấu hình GROQ_API_KEY."
    
    # Prompt chi tiết để AI làm rõ tính chất từ
    prompt = f"""
    Hãy phân tích từ tiếng Nga: '{word_ru}' (nghĩa: {word_vn}).
    Yêu cầu trình bày theo cấu trúc sau bằng tiếng Việt:
    1. Loại từ (Động từ/Danh từ/Tính từ...).
    2. Nếu là Động từ: Nói rõ ý nghĩa, ngữ cảnh sử dụng (hoàn thành/chưa hoàn thành), chia động từ theo các ngôi (я, ты, он/она, мы, вы, они).
    3. Nếu là Danh từ: Cho biết giống, chia ở số ít và số nhiều (cách 1).
    4. Nếu là Tính từ/Trạng từ: Giải thích cách dùng và các biến thể.
    5. Đặt 2 câu ví dụ bằng TIẾNG NGA (có dịch tiếng Việt):
       - 1 câu đời thường.
       - 1 câu liên quan đến quân sự hoặc kỹ thuật quân sự.
    """
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Bạn là chuyên gia ngôn ngữ Nga chuyên ngành quân sự. Hãy trả lời cực kỳ chi tiết về ngữ pháp."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Lỗi từ AI: {response.text}"
    except Exception as e:
        return f"Lỗi kết nối: {str(e)}"

# --- 2. QUẢN LÝ DỮ LIỆU ---
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'data' not in st.session_state: st.session_state.data = None
if 'show_analysis' not in st.session_state: st.session_state.show_analysis = False

with st.sidebar:
    st.header("⚙️ Cấu hình")
    uploaded_file = st.file_uploader("Nạp file Excel từ vựng", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        df.columns = [str(c).strip().lower() for c in df.columns]
        # XÁO TRỘN NGẪU NHIÊN NGAY KHI NẠP FILE
        st.session_state.data = df.sample(frac=1).reset_index(drop=True)
        st.success("✅ Đã nạp và xáo trộn từ vựng!")

# --- 3. GIAO DIỆN HỌC ---
st.title("🇷🇺 Russian Deep Learning")

if st.session_state.data is not None:
    df = st.session_state.data
    col_ru = next((c for c in df.columns if any(k in c for k in ['nga', 'ru'])), None)
    col_vn = next((c for c in df.columns if any(k in c for k in ['việt', 'vn', 'viet'])), None)

    if col_ru and col_vn:
        row = df.iloc[st.session_state.idx]
        word_vn, word_ru = str(row[col_vn]).strip(), str(row[col_ru]).strip()

        st.markdown(f"### Dịch sang tiếng Nga: <span style='color:#007bff'>{word_vn}</span>", unsafe_allow_html=True)
        user_input = st.text_input("Gõ đáp án:", key=f"in_{st.session_state.idx}")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Kiểm tra & Phân tích chuyên sâu 🧠"):
                st.session_state.show_analysis = True
                if user_input.strip().lower() == word_ru.lower():
                    st.success(f"⭐ Chính xác! Đáp án là: {word_ru}")
                else:
                    st.error(f"❌ Sai rồi. Đáp án đúng: {word_ru}")

        with c2:
            if st.button("Từ tiếp theo (Ngẫu nhiên) ➡️"):
                st.session_state.idx = random.randint(0, len(df)-1)
                st.session_state.show_analysis = False
                st.rerun()

        # HIỂN THỊ PHÂN TÍCH CHI TIẾT
        if st.session_state.show_analysis:
            with st.spinner("🤖 AI đang phân tích chi tiết ngữ pháp..."):
                analysis = call_ai_analysis(word_ru, word_vn)
                st.markdown("---")
                st.markdown("#### 📝 Báo cáo phân tích ngữ pháp")
                st.write(analysis)
    else:
        st.error("File Excel cần có cột 'Tiếng Nga' và 'Tiếng Việt'.")
else:
    st.info("👋 Hãy tải file Excel lên ở thanh bên trái để bắt đầu bài học xáo trộn.")
