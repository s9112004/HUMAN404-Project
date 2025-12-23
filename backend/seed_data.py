import os
import mysql.connector
from dotenv import load_dotenv

# 1. 載入 .env 設定
load_dotenv()

def init_db():
    print("🔄 正在嘗試連線至 AWS RDS...")
    
    conn = None
    try:
        # 建立連線
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = conn.cursor()
        print("✅ 連線成功！(AWS 防火牆與帳密驗證通過)")

        # 2. 建立資料表
        print("🛠️  正在建立資料表 document_store...")
        create_table_query = """
        CREATE TABLE IF NOT EXISTS document_store (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)

        # 3. 準備測試資料
        print("📝 正在寫入測試資料...")
        sample_data = [
            ('AWS費用政策', 'RDS 的費用包含執行個體工時與儲存空間。建議使用 Reserved Instances 省錢。'),
            ('專案Alpha部署', '專案Alpha 目前部署於 us-east-1。使用 Docker 技術，Port 為 8080。'),
            ('MCP開發指南', 'MCP (Model Context Protocol) 是用來連接 AI 模型與資料庫的標準協議。'),
            ('API串接說明', '所有 API 請求需帶上 Bearer Token，並使用 HTTPS 加密傳輸。')
        ]

        # 4. 執行寫入
        insert_query = "INSERT INTO document_store (title, content) VALUES (%s, %s)"
        cursor.executemany(insert_query, sample_data)
        conn.commit()
        
        print(f"🎉 成功！已寫入 {cursor.rowcount} 筆資料。你的資料庫準備好了！")

    except mysql.connector.Error as err:
        print(f"❌ 發生錯誤: {err}")
        print("💡 PM 提示: 請檢查 Security Group 是否開放 My IP (Port 3306)，或 .env 密碼是否正確。")
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    init_db()