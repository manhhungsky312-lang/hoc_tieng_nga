def call_gemini_analysis(word_ru, word_vn):
    """Gọi trực tiếp Gemini API - Bản sửa lỗi 404 và v1beta"""
    if not api_key: return "Thiếu API Key trong cấu hình Secrets."
    
    # Thử gọi bản v1 (ổn định nhất) thay vì v1beta
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    
    prompt = f"""
    Bạn là giảng viên tiếng Nga quân sự. Hãy phân tích từ: '{word_ru}' ({word_vn}).
    Yêu cầu chính xác 100%:
    1. LOẠI TỪ và GIỐNG (Nếu là danh từ: -а/-я là CÁI; phụ âm là ĐỰC; -о/-е là TRUNG).
    2. BIẾN CÁCH: Chia số ít và số nhiều (Cách 1).
    3. ĐỘNG TỪ: Chia đủ 6 ngôi hiện tại.
    4. VÍ DỤ: 1 câu đời thường + 1 câu QUÂN SỰ thực tế (Nga - Việt).
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1}
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        # Nếu v1 vẫn báo 404, thử lùi về v1beta (dành cho một số tài khoản mới)
        if response.status_code == 404:
            url_beta = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            response = requests.post(url_beta, headers=headers, data=json.dumps(payload))
            
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Lỗi Google ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Lỗi kết nối: {str(e)}"
