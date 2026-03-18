import streamlit as st
import pandas as pd
import requests

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Học Tiếng Nga Quân Sự v3", layout="centered")

api_key = st.secrets.get("GROQ_API_KEY")

def call_ai_analysis(word_ru, word_vn):
    if not api_key: return "Chưa cấu hình API Key."
    
    # PROMPT KHẮT KHE: ÉP AI KIỂM TRA QUY TẮC GIỐNG DANH TỪ
    prompt = f"""
    Hãy phân tích từ tiếng Nga: '{word_ru}' (nghĩa tiếng Việt: {word_vn}).
    Yêu cầu trình bày cực kỳ chính xác theo các bước sau:
    1. Xác định LOẠI TỪ. 
    2. Nếu là DANH TỪ: Phải xác định đúng GIỐNG (Đực/Cái/Trung) dựa trên đuôi từ. Ví dụ: -a/-я là Giống Cái; phụ âm/-й là Giống Đực; -о/-е là Giống Trung. Chia số ít và số nhiều (Cách 1).
    3. Nếu là ĐỘNG TỪ: Xác định cặp khía cạnh. Chia động từ thời hiện tại cho tất cả các ngôi (я, ты, он/она, мы, вы, они).
    4. Ví dụ: Đặt 1 câu đời thường và 1 câu chuyên ngành QUÂN SỰ (Tiếng Nga có dịch tiếng Việt).
    Lưu ý: Không được nhầm lẫn giống của danh từ. Trình bày bằng tiếng Việt rõ ràng.
    """
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Bạn là giáo sư ngôn ngữ Nga tại Học viện Kỹ thuật Quân sự. Trả lời chính xác, học thuật, không sai kiến thức căn bản."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0 # Mức chính xác tuyệt đối, không sáng tạo lung tung
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.json()['choices'][0]['message']['content']
    except: return "Lỗi kết nối AI. Vui lòng thử lại."

# --- 2. KHÓA TRẠNG THÁI (NGĂN NHẢY CÂU) ---
if 'data' not in st.session_state: st.session_state.data = None
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'show_analysis' not in st.session_state: st.session_state.show_analysis = False
if 'user_ans' not in st.session_state: st.session_state.user_ans = ""

# --- 3. SIDEBAR ---
with st.sidebar:
    st.header("Cài đặt")
    uploaded_file = st.file_uploader("Nạp file Excel", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        df.columns = [str(c).strip().lower() for c in df.columns]
        # Xáo trộn ngẫu nhiên một lần duy nhất khi nạp file
        st.session_state.data = df.sample(frac=1).reset_index(drop=True)
        st.session_state.idx = 0
        st.session_state.show_analysis = False
        st.success("Đã nạp và xáo trộn từ vựng!")

# --- 4. GIAO DIỆN CHÍNH ---
st.title("🇷🇺 Russian Deep Learning")

if st.session_state.data is not None:
    df = st.session_state.data
    col_ru = next((c for c in df.columns if any(k in c for k in ['nga', 'ru'])), None)
    col_vn = next((c for c in df.columns if any(k in c for k in ['việt', 'vn', 'viet'])), None)

    if col_ru and col_vn:
        row = df.iloc[st.session_state.idx]
        word_ru = str(row[col_ru]).strip()
        word_vn = str(row[col_vn]).strip()

        st.write(f"**Câu hỏi {st.session_state.idx + 1} / {len(df)}**")
        st.markdown(f"### Dịch sang tiếng Nga: <span style='color:#d32f2f'>{word_vn}</span>", unsafe_allow_html=True)

        # Nhập liệu không dùng Form để xử lý mượt hơn nhưng có khóa trạng thái
        user_input = st.text_input("Nhập đáp án:", key=f"input_{st.session_state.idx}")

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Kiểm tra ✅"):
                if user_input.strip().lower() == word_ru.lower():
                    st.success(f"Chính xác! Đáp án là: {word_ru}")
                else:
                    st.error(f"Sai rồi. Đáp án đúng phải là: {word_ru}")
                st.session_state.show_analysis = True

        with col_b:
            if st.button("Từ tiếp theo ➡️"):
                if st.session_state.idx < len(df) - 1:
                    st.session_state.idx += 1
                else:
                    st.session_state.idx = 0
                st.session_state.show_analysis = False
                st.rerun()

        # Chỉ hiển thị phân tích khi người dùng đã bấm Kiểm tra
        if st.session_state.show_analysis:
            with st.spinner("AI đang phân tích ngữ pháp chi tiết..."):
                result = call_ai_analysis(word_ru, word_vn)
                st.markdown("---")
                st.markdown(result)
    else:
        st.error("File Excel thiếu cột Tiếng Nga/Việt.")
else:
    st.info("Mời bạn nạp file Excel ở thanh bên trái.")
