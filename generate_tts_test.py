import os
import requests

vi_banking_cases = [
    "Ngân hàng VCB xin thông báo số dư tài khoản của bạn là 15.500.000đ.",
    "Mã xác thực giao dịch của bạn là 123456. Vui lòng không cung cấp mã này cho bất kỳ ai.",
    "BIDV kính chào quý khách. Giao dịch rút tiền 2.000.000đ đã được thực hiện thành công.",
    "Thẻ tín dụng TCB của quý khách sắp đến hạn thanh toán vào ngày 15/09/2024.",
    "Vui lòng nhập 3 số CVV ở mặt sau thẻ để hoàn tất giao dịch.",
    "Ông John Smith đã chuyển khoản 500.000đ vào tài khoản của bạn lúc 14:30.",
    "Hạn mức thẻ VPB của quý khách vừa được nâng lên 50.000.000đ.",
    "Cảnh báo lừa đảo: MBB không bao giờ yêu cầu khách hàng cung cấp mã CVC.",
    "Để tra cứu số dư, quý khách vui lòng gọi đến tổng đài 1900545415 hoặc số điện thoại hỗ trợ 0987654321.",
    "Khách hàng Nguyễn Văn A có khoản vay đến hạn thanh toán vào ngày 31/12/2024.",
    "Tỷ giá USD hôm nay là 25.400đ cho 1 đô la.",
    "Bạn vừa nhận được $500 từ nước ngoài gửi về.",
    "Giao dịch chuyển tiền từ VTB sang ACB đã thành công.",
    "Mật khẩu thẻ ATM của bạn đã bị khóa sau 3 lần nhập sai.",
    "Lãi suất tiết kiệm kỳ hạn 12 tháng tại Agribank hiện là 5.5% một năm.",
    "VIB khuyến mãi hoàn tiền 10% khi chi tiêu qua thẻ tín dụng.",
    "Giao dịch trị giá 3.500.000 VNĐ đang chờ xử lý.",
    "Cảm ơn bạn đã sử dụng dịch vụ ngân hàng điện tử của SHB.",
    "Tài khoản của bạn vừa bị trừ 50.000đ phí duy trì thẻ hàng tháng.",
    "Quý khách vui lòng kiểm tra kỹ số tài khoản người nhận trước khi chuyển tiền."
]

en_banking_cases = [
    "VCB bank informs you that your account balance is 15,500,000 VND.",
    "Your transaction verification code is 123456. Please do not share it with anyone.",
    "BIDV welcomes you. A cash withdrawal of 2,000,000 VND has been processed successfully.",
    "Your TCB credit card payment is due on 15/09/2024.",
    "Please enter the 3-digit CVV on the back of your card to complete the transaction.",
    "Mr. Nguyen Van A has transferred 500,000 VND to your account at 14:30.",
    "Your VPB card limit has just been increased to 50,000,000 VND.",
    "Fraud warning: MBB will never ask customers to provide their CVC code.",
    "To check your balance, please call our hotline at 1900545415 or our support number 0987654321.",
    "Customer John Smith has a loan payment due on 31/12/2024.",
    "The USD exchange rate today is 25,400 VND for $1.",
    "You have just received $500 from an overseas transfer.",
    "The money transfer from VTB to ACB was successful.",
    "Your ATM card PIN has been locked after 3 incorrect attempts.",
    "The 12-month savings interest rate at Agribank is currently 5.5% per year.",
    "VIB offers 10% cashback on credit card spending.",
    "A transaction worth 3,500,000 VND is pending.",
    "Thank you for using SHB electronic banking services.",
    "Your account has been charged 50,000 VND for the monthly card maintenance fee.",
    "Please double-check the recipient's account number before transferring money."
]

# Generate more cases to reach a larger pool if needed
for i in range(1, 21):
    vi_banking_cases.append(f"Giao dịch số {i} ngày hôm nay đã được ghi nhận vào hệ thống ngân hàng.")
    en_banking_cases.append(f"Transaction number {i} today has been recorded in the banking system.")

API_URL = "http://localhost:9000/api/v1/tts"
OUTPUT_DIR = "test_outputs"

os.makedirs(OUTPUT_DIR, exist_ok=True)

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Banking TTS Test Output</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 30px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        audio { height: 30px; }
    </style>
</head>
<body>
    <h1>Banking TTS Test Output</h1>
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

print("Generating Vietnamese Banking test cases...")
html_content += "<h2>Vietnamese</h2><table><tr><th>Index</th><th>Text</th><th>Audio</th></tr>"
for i, text in enumerate(vi_banking_cases):
    filename = generate_audio(text, "vi", i + 1)
    if filename:
        html_content += f"<tr><td>{i+1}</td><td>{text}</td><td><audio controls src='{filename}'></audio></td></tr>"
html_content += "</table>"

print("Generating English Banking test cases...")
html_content += "<h2>English</h2><table><tr><th>Index</th><th>Text</th><th>Audio</th></tr>"
for i, text in enumerate(en_banking_cases):
    filename = generate_audio(text, "en", i + 1)
    if filename:
        html_content += f"<tr><td>{i+1}</td><td>{text}</td><td><audio controls src='{filename}'></audio></td></tr>"
html_content += "</table>"

html_content += "</body></html>"

with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"\\nTest generation complete. Open {os.path.abspath(os.path.join(OUTPUT_DIR, 'index.html'))} to listen to the results.")
