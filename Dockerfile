
# Sử dụng Python 3.10 làm image cơ sở
FROM python:3.10-slim

# Đặt thư mục làm việc trong container
WORKDIR /app

# Sao chép file requirements.txt vào container
COPY requirements.txt .

# Cài đặt các gói cần thiết từ requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn vào container
COPY . .

# Expose cổng 5000 để Flask lắng nghe
EXPOSE 5000

# Chạy ứng dụng Flask
CMD ["python", "flask_app.py"]
