# 1. 使用 Python 輕量版作為基地
FROM python:3.10-slim

# 2. 設定容器內的工作資料夾
WORKDIR /app

# 3. 先複製 requirements.txt 並安裝 (利用 Cache 加速)
COPY requirements.txt .
# 這裡加一個指令確保 pip 是新的，並安裝套件
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 4. 複製你的核心檔案與設定檔
COPY server.py .
COPY .env .

# 5. 設定容器對外公開的 Port (假設你的 server.py 是跑 8000)
# 如果你的程式是跑 5000，請自行改成 5000
EXPOSE 8000

# 6. 啟動指令：直接執行 server.py
CMD ["python", "server.py"]