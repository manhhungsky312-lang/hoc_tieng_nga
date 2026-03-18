import streamlit as st
import pandas as pd
import requests

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Học Tiếng Nga Quân Sự v4", layout="centered")

api_key = st.secrets.get("GROQ_API_KEY")

def call_ai_analysis(word_ru, word_vn):
    if not api_key: return "Chưa cấu hình API Key."
    
    # PROMPT ÉP AI PHẢI KIỂM TRA BẢNG GIỐNG (GENDER RULES)
    prompt = f"""
    Hãy phân tích từ tiếng Nga: '{word_ru}' (nghĩa: {word_vn}).
    Yêu cầu trình bày CHÍNH XÁC 100% theo quy tắc ngữ pháp:
    1. LOẠI TỪ.
    2. GIỐNG (Nếu là danh từ): Phải xác định đúng giống Đực/Cái/Trung dựa trên đuôi từ ở số ít (Ví dụ: -ы/-и là dấu hiệu số nhiều của giống Đực hoặc Cái, không bao giờ là giống Trung).
    3. BIẾN CÁCH: Chia số ít và số nhiều (Cách 1).
    4. ĐỘNG TỪ: Chia đủ 6 ngôi hiện tại: я, ты, он/она, мы, вы, они.
    5. VÍ DỤ: 1 câu đời thường và 1 câu QUÂN SỰ thực tế (Tiếng Nga + Dịch Việt).
    """
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Bạn là giáo sư ngôn ngữ Nga tại Học viện Quân sự. Trả lời cực kỳ chính xác, không được sai kiến thức về giống và số của danh từ."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.json()['choices'][0]['message']['content']
    except: return "Lỗi hệ thống AI."

# --- 2. KHÓA TRẠNG THÁI DỮ LIỆU (QUAN TRỌNG NHẤT) ---
if 'data_list' not in st.session_state: st.session_state.data_list = None
if 'current_idx' not in st.session_state: st.session_state.current_idx = 0
if 'is_checked' not in st.session_state: st.session_state.is_checked = False

# --- 3. SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Cài đặt")
    uploaded_file = st.file_uploader("Nạp file Excel", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        df.columns = [str(c).strip().lower() for c in df.columns]
        # Xáo trộn và lưu vào danh sách cố định trong session_state
        st.session_state.data_list = df.sample(frac=1).reset_index(drop=True)
        st.session_state.current_idx = 0
        st.session_state.is_checked = False
        st.success("Đã nạp và khóa danh sách câu hỏi!")

# --- 4. GIAO DIỆN HỌC TẬP ---
st.title("🇷🇺 Russian Training v4")

if st.session_state.data_list is not None:
    df = st.session_state.data_list
    col_ru = next((c for c in df.columns if any(k in c for k in ['nga', 'ru'])), None)
    col_vn = next((c for c in df.columns if any(k in c for k in ['việt', 'vn', 'viet'])), None)

    if col_ru and col_vn:
        # Lấy dữ liệu từ danh sách đã khóa
        row = df.iloc[st.session_state.current_idx]
        word_ru = str(row[col_ru]).strip()
        word_vn = str(row[col_vn]).strip()

        st.info(f"Câu hỏi: {st.session_state.current_idx + 1} / {len(df)}")
        st.markdown(f"### Dịch sang tiếng Nga: **{word_vn}**")

        # Dùng form để ép Streamlit không được tự ý chạy lại khi đang nhập liệu
        with st.form(key=f"study_form_{st.session_state.current_idx}"):
            user_input = st.text_input("Nhập từ tiếng Nga:", value="")
            btn_submit = st.form_submit_button("KIỂM TRA ✅")

        if btn_submit:
            st.session_state.is_checked = True
            if user_input.strip().lower() == word_ru.lower():
                st.success(f"⭐ CHÍNH XÁC! Đáp án: {word_ru}")
            else:
                st.error(f"❌ SAI RỒI! Đáp án đúng: {word_ru}")

            with st.spinner("AI đang phân tích ngữ pháp quân sự..."):
                analysis = call_ai_analysis(word_ru, word_vn)
                st.markdown("---")
                st.info(analysis)

        # Nút chuyển câu chỉ hiện sau khi đã Kiểm tra
        if st.session_state.is_checked:
            if st.button("Từ tiếp theo ➡️"):
                if st.session_state.current_idx < len(df) - 1:
                    st.session_state.current_idx += 1
                else:
                    st.session_state.current_idx = 0
                st.session_state.is_checked = False
                st.rerun()
    else:
        st.error("File Excel thiếu cột Tiếng Nga hoặc Tiếng Việt.")
else:
    st.write("Mời bạn nạp file Excel ở Menu bên trái.")
