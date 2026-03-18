import streamlit as st
import pandas as pd
import requests
import random

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Học Tiếng Nga Chuyên Sâu", layout="wide")

api_key = st.secrets.get("GROQ_API_KEY")

# --- 2. HÀM GỌI AI CHUYÊN GIA (PROMPT ĐÃ NÂNG CẤP) ---
def call_ai_analysis(word_ru, word_vn):
    if not api_key: return "Chưa cấu hình API Key."
    
    # Ép AI phải trả lời theo cấu trúc học thuật nghiêm túc
    prompt = f"""
    Bạn là một giảng viên tiếng Nga kỳ cựu. Hãy phân tích từ: '{word_ru}' (nghĩa: {word_vn}).
    Yêu cầu trình bày cực kỳ chính xác:
    1. Loại từ và Giống (nếu là danh từ).
    2. Nếu là Động từ: Cho biết cặp khía cạnh (Hoàn thành/Chưa hoàn thành). Chia động từ ở thời HIỆN TẠI (hoặc TƯƠNG LAI đơn) theo 6 ngôi: я, ты, он/она, мы, вы, они.
    3. Nếu là Danh từ: Chia ở số ít và số nhiều (Cách 1).
    4. Ví dụ: Đặt 2 câu bằng TIẾNG NGA (có dịch tiếng Việt):
       - 1 câu đời thường.
       - 1 câu chuyên ngành QUÂN SỰ hoặc KỸ THUẬT.
    Chú ý: Tuyệt đối không nhầm lẫn về giống và cách chia.
    """
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Bạn là chuyên gia ngôn ngữ Nga quân sự. Trình bày rõ ràng, học thuật."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1 # Giảm độ sáng tạo để tăng độ chính xác tuyệt đối
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.json()['choices'][0]['message']['content'] if response.status_code == 200 else "Lỗi kết nối AI."
    except: return "Lỗi hệ thống."

# --- 3. QUẢN LÝ TRẠNG THÁI (SỬA LỖI NHẢY CÂU) ---
if 'data' not in st.session_state: st.session_state.data = None
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'ans_status' not in st.session_state: st.session_state.ans_status = None

# --- 4. GIAO DIỆN ---
with st.sidebar:
    st.header("⚙️ Dữ liệu")
    uploaded_file = st.file_uploader("Nạp file Excel", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        df.columns = [str(c).strip().lower() for c in df.columns]
        # Xáo trộn và lưu vào session_state một lần duy nhất
        st.session_state.data = df.sample(frac=1).reset_index(drop=True)
        st.session_state.idx = 0
        st.success("Đã xáo trộn danh sách!")

st.title("🇷🇺 Russian Military Learning")

if st.session_state.data is not None:
    df = st.session_state.data
    col_ru = next((c for c in df.columns if any(k in c for k in ['nga', 'ru'])), None)
    col_vn = next((c for c in df.columns if any(k in c for k in ['việt', 'vn', 'viet'])), None)

    if col_ru and col_vn:
        current_row = df.iloc[st.session_state.idx]
        correct_word = str(current_row[col_ru]).strip()
        display_vn = str(current_row[col_vn]).strip()

        st.info(f"Câu hỏi số {st.session_state.idx + 1} / {len(df)}")
        st.markdown(f"### Dịch sang tiếng Nga: **{display_vn}**")
        
        # Dùng form để ngăn chặn việc tự động load lại khi đang gõ
        with st.form(key=f"word_form_{st.session_state.idx}"):
            user_input = st.text_input("Nhập từ tiếng Nga:", value="")
            submit_btn = st.form_submit_button("Kiểm tra ✅")

        if submit_btn:
            # So sánh không phân biệt hoa thường và khoảng trắng thừa
            if user_input.strip().lower() == correct_word.lower():
                st.success(f"⭐ CHÍNH XÁC! Đáp án: {correct_word}")
                st.session_state.ans_status = "correct"
            else:
                st.error(f"❌ SAI. Đáp án đúng là: {correct_word}")
                st.session_state.ans_status = "wrong"
            
            with st.spinner("Đang phân tích chuyên sâu..."):
                analysis = call_ai_analysis(correct_word, display_vn)
                st.markdown("---")
                st.markdown(analysis)

        if st.button("Từ tiếp theo ➡️"):
            if st.session_state.idx < len(df) - 1:
                st.session_state.idx += 1
            else:
                st.session_state.idx = 0 # Quay lại từ đầu nếu hết
            st.rerun()
    else:
        st.error("File thiếu cột 'Tiếng Nga' hoặc 'Tiếng Việt'.")
else:
    st.write("Hãy nạp file Excel để bắt đầu.")
