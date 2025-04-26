import os
import shutil
import smtplib
import schedule
import time
from email.message import EmailMessage
from dotenv import load_dotenv
from datetime import datetime

# Load thông tin từ file .env
load_dotenv()

# Lấy giá trị từ file .env
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

SOURCE_DIR = '.'            # Thư mục chứa file database
BACKUP_DIR = 'backups'      # Thư mục lưu file backup

def send_email(subject, body):
    try:
        msg = EmailMessage()
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        msg['Subject'] = subject
        msg.set_content(body)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)

        print("✅ Email đã được gửi.")
    except Exception as e:
        print("❌ Gửi email thất bại:", str(e))

def backup_database():
    try:
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)

        backed_up_files = []
        for filename in os.listdir(SOURCE_DIR):
            if filename.endswith(".sql") or filename.endswith(".sqlite3"):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                src = os.path.join(SOURCE_DIR, filename)
                dst = os.path.join(BACKUP_DIR, f"{filename.rsplit('.', 1)[0]}_{timestamp}.{filename.rsplit('.', 1)[1]}")
                shutil.copy2(src, dst)
                backed_up_files.append(os.path.basename(dst))

        if backed_up_files:
            message = "Backup thành công các file:\n" + "\n".join(backed_up_files)
            send_email("✅ Backup thành công", message)
        else:
            send_email("⚠️ Không có file để backup", "Không tìm thấy file .sql hoặc .sqlite3 trong thư mục.")
    except Exception as e:
        send_email("❌ Backup thất bại", f"Lỗi: {str(e)}")

# Lên lịch chạy lúc 00:00 hàng ngày
schedule.every().day.at("00:00").do(backup_database)

print("🕛 Script đang chạy... Chờ đến 00:00 mỗi ngày để backup.")

while True:
    schedule.run_pending()
    time.sleep(60)
