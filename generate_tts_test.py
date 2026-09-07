import os
import requests

vi_templates = [
    "Xin chào, đây là câu thử nghiệm số {}.",
    "Hôm nay là ngày {}, thời tiết rất đẹp.",
    "Sản phẩm này có giá {} VNĐ.",
    "Số điện thoại liên hệ là 09{} 123 456.",
    "Khoảng {} người đã tham gia sự kiện này.",
    "Bây giờ là {} giờ {} phút.",
    "Tôi đã mua {} quyển sách với giá {} nghìn đồng.",
    "Cửa hàng mở cửa từ {} giờ sáng đến {} giờ tối.",
    "Theo dự báo, nhiệt độ hôm nay khoảng {} độ C.",
    "Dự án này dự kiến hoàn thành trong {} tháng."
]

en_templates = [
    "Hello, this is test sentence number {}.",
    "Today is day {}, and the weather is beautiful.",
    "This product costs {} dollars.",
    "The contact number is 1-800-{}-1234.",
    "Approximately {} people attended the event.",
    "The time is now {}:{} PM.",
    "I bought {} books for {} dollars.",
    "The store is open from {} AM to {} PM.",
    "According to the forecast, the temperature is {} degrees.",
    "This project is expected to be completed in {} months."
]

import random

vi_sentences = []
en_sentences = []

for i in range(1, 101):
    t = vi_templates[i % len(vi_templates)]
    if t.count("{}") == 1:
        vi_sentences.append(t.format(i))
    elif t.count("{}") == 2:
        vi_sentences.append(t.format(i, random.randint(1, 60)))
        
    te = en_templates[i % len(en_templates)]
    if te.count("{}") == 1:
        en_sentences.append(te.format(i))
    elif te.count("{}") == 2:
        en_sentences.append(te.format(i, random.randint(1, 60)))

vi_edge_cases = [
    "UBND TP Hà Nội vừa ban hành quyết định mới.",
    "Tôi đang học AI và Machine Learning tại ĐH Bách Khoa.",
    "Kênh VTV3 đang phát sóng chương trình thời sự lúc 19h.",
    "Giá vàng SJC hôm nay tăng mạnh, chạm mốc 80 triệu đồng/lượng.",
    "Bạn có thể gửi file PDF này qua email cho tôi được không?",
    "Anh ấy đã mua chiếc xe BMW với giá hơn 2 tỷ VNĐ.",
    "GDP quý 3 năm nay dự kiến tăng 5.5%.",
    "Ngày 31/12/2023, công ty đã tổ chức Year End Party.",
    "Website của chúng tôi là vi-en-u-e chấm com.",
    "Xin lỗi, tôi không thể tham gia meeting vào ngày mai."
]
vi_sentences = vi_edge_cases + vi_sentences[:90]

en_edge_cases = [
    "The API responds in JSON format.",
    "I love using FastAPI for building backend services.",
    "We need to deploy this Docker container on AWS EC2.",
    "The quick brown fox jumps over the lazy dog.",
    "IBM and Microsoft announced a new partnership today.",
    "My email is example@gmail.com, please contact me.",
    "The CPU usage spiked to 99% during the test.",
    "She bought an Apple Watch Series 9 yesterday.",
    "He won 1,000,000 dollars in the lottery.",
    "Welcome to the VieNeu TTS testing suite."
]
en_sentences = en_edge_cases + en_sentences[:90]

vi_sentences = vi_sentences[:100]
en_sentences = en_sentences[:100]

API_URL = "http://localhost:9000/api/v1/tts"
OUTPUT_DIR = "test_outputs"

os.makedirs(OUTPUT_DIR, exist_ok=True)

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VieNeu TTS Test Output</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 30px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        audio { height: 30px; }
    </style>
</head>
<body>
    <h1>VieNeu TTS Test Output</h1>
"""

def generate_audio(text, lang, index):
    filename = f"{lang}_{index:03d}.wav"
    filepath = os.path.join(OUTPUT_DIR, filename)
    payload = {"text": text, "language": lang}
    
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        if response.status_code == 200:
            with open(filepath, "wb") as f:
                f.write(response.content)
            print(f"Generated: {filename}")
            return filename
        else:
            print(f"Failed to generate {filename}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error generating {filename}: {e}")
        return None

print("Generating Vietnamese test cases...")
html_content += "<h2>Vietnamese (100 sentences)</h2><table><tr><th>Index</th><th>Text</th><th>Audio</th></tr>"
for i, text in enumerate(vi_sentences):
    filename = generate_audio(text, "vi", i + 1)
    if filename:
        html_content += f"<tr><td>{i+1}</td><td>{text}</td><td><audio controls src='{filename}'></audio></td></tr>"
html_content += "</table>"

print("Generating English test cases...")
html_content += "<h2>English (100 sentences)</h2><table><tr><th>Index</th><th>Text</th><th>Audio</th></tr>"
for i, text in enumerate(en_sentences):
    filename = generate_audio(text, "en", i + 1)
    if filename:
        html_content += f"<tr><td>{i+1}</td><td>{text}</td><td><audio controls src='{filename}'></audio></td></tr>"
html_content += "</table>"

html_content += "</body></html>"

with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"\\nTest generation complete. Open {os.path.abspath(os.path.join(OUTPUT_DIR, 'index.html'))} to listen to the results.")
