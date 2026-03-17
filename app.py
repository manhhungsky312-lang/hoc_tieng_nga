def call_gemini_direct(prompt):
    if not api_key:
        return "Lỗi: Chưa cấu hình API Key."
    
    # THAY ĐỔI QUAN TRỌNG: Dùng v1 (bản chính thức) thay vì v1beta
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload) # Dùng json=payload cho sạch
        if response.status_code == 200:
            res_json = response.json()
            return res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            # Nếu v1 vẫn lỗi, thử dùng model gemini-pro (bản cũ nhưng cực kỳ ổn định)
            url_backup = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={api_key}"
            response_backup = requests.post(url_backup, headers=headers, json=payload)
            if response_backup.status_code == 200:
                return response_backup.json()['candidates'][0]['content']['parts'][0]['text']
            
            return f"Lỗi Google: {response.text}"
    except Exception as e:
        return f"Lỗi kết nối: {str(e)}"
