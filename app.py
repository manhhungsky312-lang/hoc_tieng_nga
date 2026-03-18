import streamlit as st
import pandas as pd
import requests
import json

# --- 1. CẤU HÌNH ---
st.set_page_config(page_title="Học Tiếng Nga Tự Nhiên", layout="wide")
api_key = st.secrets.get("GEMINI_API_KEY")

def call_gemini_natural(word_ru, word_vn):
    """Gọi Gemini phân tích ngữ pháp chuẩn và đặt câu tự nhiên"""
    if not api_key: return "Chưa cấu hình API Key."
    
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    # PROMPT MỚI: ƯU TIÊN TÍNH TỰ NHIÊN VÀ CẤU TRÚC NGƯỜI NGA DÙNG
    prompt = f"""
    Hãy phân tích từ tiếng Nga: '{word_ru}' (nghĩa: {word_vn}).
    Yêu cầu trình bày chính xác bằng tiếng Việt:

    ### 📝 NGỮ PHÁP CHI TIẾT
    * **Loại từ & Giống:** (Nếu là danh từ, xác định Đực/Cái/Trung dựa trên đuôi -а/-я là Cái, phụ âm là Đực, -о/-е là Trung).
    * **Biến cách (Cách 1):** Chia rõ dạng Số ít và Số nhiều.
    * **Động từ (Nếu có):** Cặp khía cạnh và chia đủ 6 ngôi hiện tại (я, ты, он/она, мы, вы, они).

    ### 💬 CÁCH DÙNG TỰ NHIÊN
    * **Ví dụ 1:** Đặt một câu ngắn gọn, thông dụng mà người Nga hay dùng hàng ngày.
    * **Ví dụ 2:** Đặt một câu có cấu trúc ngữ pháp phổ biến (sử dụng cách hoặc giới từ đi kèm).
    *(Tất cả ví dụ phải có bản tiếng Nga và dịch nghĩa tiếng Việt sát nghĩa nhất).*
    """
    
    payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.2}}
    
    try:
        response = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        return f"Lỗi AI ({response.status_code})"
    except: return "Lỗi kết nối máy chủ."

# --- 2. QUẢN LÝ TRẠNG THÁI (NGĂN NHẢY CÂU) ---
if 'vocab_list' not in st.session_state: st.session_state.vocab_list = None
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'checked' not in st.session_state: st.session_state.checked = False

with st.sidebar:
    st.header("⚙️ Cài đặt")
    uploaded_file = st.file_uploader("Nạp file Excel vựng", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        df.columns = [str(c).strip().lower() for c in df.columns]
        # Xáo trộn và khóa cố định
        st.session_state.vocab_list = df.sample(frac=1).reset_index(drop=True)
        st.session_state.idx = 0
        st.session_state.checked = False
        st.success("Đã nạp danh sách ngẫu nhiên!")

# --- 3. GIAO DIỆN HỌC ---
st.title("🇷🇺 Luyện Tiếng Nga Bản Xứ")

if st.session_state.vocab_list is not None:
    data = st.session_state.vocab_list
    c_ru = next((c for c in data.columns if any(k in c for k in ['nga', 'ru'])), None)
    c_vn = next((c for c in data.columns if any(k in c for k in ['việt', 'vn', 'viet'])), None)

    if c_ru and c_vn:
        row = data.iloc[st.session_state.idx]
        word_ru = str(row[c_ru]).strip()
        word_vn = str(row[c_vn]).strip()

        st.info(f"Từ số: {st.session_state.idx + 1} / {len(data)}")
        st.subheader(f"Dịch sang tiếng Nga: {word_vn}")

        # KHÓA DỮ LIỆU BẰNG FORM THEO ID
        with st.form(key=f"native_form_{st.session_state.idx}"):
            user_input = st.text_input("Gõ đáp án:", value="")
            submit_btn = st.form_submit_button("KIỂM TRA & GIẢI THÍCH ✅")

        if submit_btn:
            st.session_state.checked = True
            if user_input.strip().lower() == word_ru.lower():
                st.success(f"Chính xác! Đáp án: {word_ru}")
            else:
                st.error(f"Sai rồi! Đáp án đúng: {word_ru}")

            with st.spinner("Gemini đang phân tích ngữ pháp tự nhiên..."):
                analysis = call_gemini_natural(word_ru, word_vn)
                st.markdown("---")
                st.markdown(analysis)

        if st.session_state.checked:
            if st.button("Học từ tiếp theo ➡️"):
                st.session_state.idx = (st.session_state.idx + 1) % len(data)
                st.session_state.checked = False
                st.rerun()
    else:
        st.error("File thiếu cột Tiếng Nga/Việt.")
else:
    st.write("Mời nạp file Excel ở thanh bên để bắt đầu bài học.")
