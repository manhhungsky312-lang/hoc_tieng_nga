import streamlit as st
import pandas as pd
import webbrowser

# --- 1. CẤU HÌNH ---
st.set_page_config(page_title="Học Tiếng Nga Siêu Tốc", layout="centered")

# --- 2. KHÓA BỘ NHỚ (NGĂN NHẢY CÂU) ---
if 'data' not in st.session_state: st.session_state.data = None
if 'idx' not in st.session_state: st.session_state.idx = 0

# --- 3. NẠP FILE ---
with st.sidebar:
    st.header("📂 Nạp từ vựng")
    uploaded_file = st.file_uploader("Chọn file Excel", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        df.columns = [str(c).strip().lower() for c in df.columns]
        # Xáo trộn 1 lần duy nhất
        st.session_state.data = df.sample(frac=1).reset_index(drop=True)
        st.session_state.idx = 0
        st.success("Đã nạp xong!")

# --- 4. GIAO DIỆN CHÍNH ---
st.title("🇷🇺 Luyện Nga Ngữ - Tra cứu Google")

if st.session_state.data is not None:
    data = st.session_state.data
    c_ru = next((c for c in data.columns if any(k in c for k in ['nga', 'ru'])), None)
    c_vn = next((c for c in data.columns if any(k in c for k in ['việt', 'vn', 'viet'])), None)

    if c_ru and c_vn:
        row = data.iloc[st.session_state.idx]
        word_ru = str(row[c_ru]).strip()
        word_vn = str(row[c_vn]).strip()

        st.info(f"Từ số {st.session_state.idx + 1} / {len(data)}")
        st.markdown(f"### Dịch sang tiếng Nga: **{word_vn}**")

        # Ô nhập liệu - Khóa theo idx
        user_input = st.text_input("Gõ từ tiếng Nga vào đây:", key=f"input_{st.session_state.idx}")

        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("KIỂM TRA ✅"):
                if user_input.strip().lower() == word_ru.lower():
                    st.success(f"Chính xác! Đáp án: {word_ru}")
                else:
                    st.error(f"Sai rồi! Đáp án: {word_ru}")

        with col2:
            # TỰ ĐỘNG TẠO LINK TRA CỨU GOOGLE
            # Bạn có thể đổi sang từ điển Wiktionary hoặc từ điển chuyên ngành khác
            search_url = f"https://www.google.com/search?q={word_ru}+nghĩa+là+gì+ngữ+pháp"
            st.link_button("TRA GOOGLE 🔍", search_url)

        with col3:
            if st.button("TỪ TIẾP THEO ➡️"):
                if st.session_state.idx < len(data) - 1:
                    st.session_state.idx += 1
                    st.rerun()
                else:
                    st.warning("Đã hết danh sách!")
    else:
        st.error("File thiếu cột Tiếng Nga/Việt.")
else:
    st.write("Mời bạn nạp file Excel ở bên trái.")
