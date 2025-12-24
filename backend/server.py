import os
import time
import mysql.connector
import uvicorn
import boto3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

# 1. 載入環境變數
load_dotenv()

# 2. 初始化 FastAPI
app = FastAPI(title="AI Assistant - AWS Full Stack Manager")

# === AWS 連線設定 ===
# 嘗試讀取 mcp-user 設定，若無則使用預設
try:
    aws_session = boto3.Session(profile_name='mcp-user', region_name='ap-northeast-1')
    print("✅ 成功載入 AWS profile: mcp-user")
except Exception:
    print("⚠️ 找不到 mcp-user，使用預設環境變數")
    aws_session = boto3.Session(region_name='ap-northeast-1')

# ===========================
#        資料定義區 (Models)
# ===========================

# --- MySQL 相關 ---
#class SearchRequest(BaseModel):(原本31、32行改成下面這個_12/23_edit)
    #keyword: str
# 修改 SearchRequest 模型
class SearchRequest(BaseModel):
    keyword: Optional[str] = None  # 變成可選，沒填就是 None
    limit: int = 10                # 預設抓 10 筆，AI 可以自己改
class AddRequest(BaseModel):
    title: str
    content: str
class UpdateRequest(BaseModel):
    id: int
    title: Optional[str] = None
    content: Optional[str] = None
class DeleteRequest(BaseModel):
    id: int

# --- S3 相關 (新增/修改/刪除) ---
class S3BucketRequest(BaseModel):
    bucket_name: str

class S3FileRequest(BaseModel):
    bucket_name: str
    file_name: str
    content: Optional[str] = "這是由 AI 自動建立的檔案內容" # 上傳時的內容

# --- EC2 相關 (新增/修改/刪除) ---
class EC2LaunchRequest(BaseModel):
    instance_type: str = "t2.micro"
    ami_id: str = "ami-0aec5ae807cea9ce0" # Ubuntu 24.04 (us-east-1)

class EC2ActionRequest(BaseModel):
    instance_id: str

class EC2ModifyRequest(BaseModel):
    instance_id: str
    new_instance_type: str # 例如改成 "t3.medium"

# ===========================
#      原有 MySQL 功能區
# ===========================
def get_conn():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"), user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"), database=os.getenv("DB_NAME")
    )
#更改原本78-85行內容邏輯有錯搜尋出來結果很奇怪_12/23_edit
@app.post("/db/search", tags=["Database"])
async def search_docs(req: SearchRequest):
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    try:
        # 1. 基礎 SQL：預設先選全部
        sql = "SELECT * FROM document_store"
        params = []

        # 2. 判斷是否過濾：如果有提供 keyword，才加上 WHERE 條件
        if req.keyword and req.keyword.strip():
            sql += " WHERE title LIKE %s OR content LIKE %s"
            # 準備參數
            params.extend([f"%{req.keyword}%", f"%{req.keyword}%"])
        
        # 3. 排序：永遠加上由舊到新排序 (解決您看資料的問題[DESC(新到舊排序)/ASC)(舊到新排序)])
        sql += " ORDER BY id ASC"

        # 4. 限制筆數：加上 LIMIT
        sql += " LIMIT %s"
        params.append(req.limit)

        # 5. 執行 SQL
        cursor.execute(sql, tuple(params))
        results = cursor.fetchall()
        
        # 6. 回傳結果
        if not results:
            return {"result": "無相關資料"}
            
        # 為了讓 AI 更好讀，我們可以簡單整理一下格式 (選擇性)
        return {"result": results}

    except Exception as e:
        return {"result": f"搜尋發生錯誤: {str(e)}"}
    finally:
        conn.close()

@app.post("/db/add", tags=["Database"])
async def add_doc(req: AddRequest):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO document_store (title, content) VALUES (%s, %s)", (req.title, req.content))
        conn.commit()
        return {"result": f"✅ 已新增: {req.title}"}
    finally: conn.close()

@app.post("/db/update", tags=["Database"])
async def update_doc(req: UpdateRequest):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        updates = []
        params = []
        if req.title: updates.append("title=%s"); params.append(req.title)
        if req.content: updates.append("content=%s"); params.append(req.content)
        if not updates: return {"result": "無修改內容"}
        params.append(req.id)
        cursor.execute(f"UPDATE document_store SET {','.join(updates)} WHERE id=%s", tuple(params))
        conn.commit()
        return {"result": f"✅ 已更新 ID: {req.id}"}
    finally: conn.close()

@app.post("/db/delete", tags=["Database"])
async def delete_doc(req: DeleteRequest):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM document_store WHERE id=%s", (req.id,))
        conn.commit()
        return {"result": f"✅ 已刪除 ID: {req.id}"}
    finally: conn.close()

# ===========================
#        S3 功能全集
# ===========================

# 1. 查找 (Read): 列出 Buckets
@app.post("/aws/s3/list_buckets", tags=["S3"], summary="列出所有 S3 Bucket")
async def s3_list_buckets():
    try:
        s3 = aws_session.client('s3')
        res = s3.list_buckets()
        names = [b['Name'] for b in res['Buckets']]
        return {"buckets": names if names else "目前沒有 Bucket"}
    except Exception as e: return {"error": str(e)}

# 2. 查找 (Read): 列出 Bucket 內的檔案
@app.post("/aws/s3/list_files", tags=["S3"], summary="列出特定 Bucket 內的檔案")
async def s3_list_files(req: S3BucketRequest):
    try:
        s3 = aws_session.client('s3')
        res = s3.list_objects_v2(Bucket=req.bucket_name)
        if 'Contents' not in res: return {"files": "空資料夾"}
        files = [f"{obj['Key']} (大小: {obj['Size']} bytes)" for obj in res['Contents']]
        return {"files": files}
    except Exception as e: return {"error": str(e)}

# 3. 新增 (Create): 建立新 Bucket
@app.post("/aws/s3/create_bucket", tags=["S3"], summary="建立新的 S3 Bucket")
async def s3_create_bucket(req: S3BucketRequest):
    try:
        s3 = aws_session.client('s3')
        # us-east-1 不需要 LocationConstraint
        s3.create_bucket(Bucket=req.bucket_name) 
        return {"result": f"✅ Bucket '{req.bucket_name}' 建立成功！"}
    except Exception as e: return {"error": str(e)}

# 4. 新增/更新 (Create/Update): 上傳或覆蓋檔案
@app.post("/aws/s3/put_file", tags=["S3"], summary="上傳文字檔 (若存在則覆蓋/更新)")
async def s3_put_file(req: S3FileRequest):
    try:
        s3 = aws_session.client('s3')
        # 將字串轉為檔案上傳
        s3.put_object(Bucket=req.bucket_name, Key=req.file_name, Body=req.content)
        return {"result": f"✅ 檔案 '{req.file_name}' 已成功寫入 '{req.bucket_name}'。"}
    except Exception as e: return {"error": str(e)}

# 5. 刪除 (Delete): 刪除檔案
@app.post("/aws/s3/delete_file", tags=["S3"], summary="刪除 S3 檔案")
async def s3_delete_file(req: S3FileRequest):
    try:
        s3 = aws_session.client('s3')
        s3.delete_object(Bucket=req.bucket_name, Key=req.file_name)
        return {"result": f"🗑️ 檔案 '{req.file_name}' 已刪除。"}
    except Exception as e: return {"error": str(e)}

# 6. 刪除 (Delete): 刪除 Bucket (必須是空的)
@app.post("/aws/s3/delete_bucket", tags=["S3"], summary="刪除 S3 Bucket")
async def s3_delete_bucket(req: S3BucketRequest):
    try:
        s3 = aws_session.client('s3')
        s3.delete_bucket(Bucket=req.bucket_name)
        return {"result": f"🗑️ Bucket '{req.bucket_name}' 已刪除。"}
    except Exception as e: return {"error": f"刪除失敗 (請確認 Bucket 是否為空): {str(e)}"}

# ===========================
#        EC2 功能全集
# ===========================

# 1. 查找 (Read): 查詢所有機器狀態
@app.post("/aws/ec2/list", tags=["EC2"], summary="查詢 EC2 列表與狀態")
async def ec2_list():
    try:
        ec2 = aws_session.client('ec2')
        res = ec2.describe_instances()
        info = []
        for r in res['Reservations']:
            for i in r['Instances']:
                name = "無名稱"
                # 嘗試讀取 Tag 中的 Name
                if 'Tags' in i:
                    for t in i['Tags']:
                        if t['Key'] == 'Name': name = t['Value']
                info.append(f"ID: {i['InstanceId']} | Name: {name} | 狀態: {i['State']['Name']} | 規格: {i['InstanceType']}")
        return {"instances": info if info else "沒有 EC2 實體"}
    except Exception as e: return {"error": str(e)}

# 2. 新增 (Create): 啟動新機器
@app.post("/aws/ec2/launch", tags=["EC2"], summary="購買並啟動 EC2")
async def ec2_launch(req: EC2LaunchRequest):
    try:
        ec2 = aws_session.resource('ec2')
        instances = ec2.create_instances(
            ImageId=req.ami_id, MinCount=1, MaxCount=1, InstanceType=req.instance_type,
            TagSpecifications=[{'ResourceType': 'instance','Tags': [{'Key': 'Name', 'Value': 'AI-Created-Server'}]}]
        )
        return {"result": f"🚀 機器啟動中，ID: {instances[0].id}"}
    except Exception as e: return {"error": str(e)}

# 3. 更新 (Update): 電源管理 (開/關/重啟)
@app.post("/aws/ec2/power", tags=["EC2"], summary="電源管理: start/stop/reboot")
async def ec2_power(req: EC2ActionRequest, action: str):
    # action 參數可透過 URL ?action=start 傳入，或 AI 自動判斷
    try:
        ec2 = aws_session.client('ec2')
        if action == "start":
            ec2.start_instances(InstanceIds=[req.instance_id])
            return {"result": f"🟢 正在啟動 {req.instance_id}..."}
        elif action == "stop":
            ec2.stop_instances(InstanceIds=[req.instance_id])
            return {"result": f"🔴 正在停止 {req.instance_id}..."}
        elif action == "reboot":
            ec2.reboot_instances(InstanceIds=[req.instance_id])
            return {"result": f"🔄 正在重啟 {req.instance_id}..."}
        else:
            return {"error": "無效的動作，請用 start, stop, 或 reboot"}
    except Exception as e: return {"error": str(e)}

# 4. 更新 (Update): 修改規格 (需先關機)
@app.post("/aws/ec2/modify_type", tags=["EC2"], summary="修改 EC2 規格 (如 t2.micro -> t3.medium)")
async def ec2_modify_type(req: EC2ModifyRequest):
    try:
        client = aws_session.client('ec2')
        
        # 1. 檢查狀態，必須是 stopped
        desc = client.describe_instances(InstanceIds=[req.instance_id])
        state = desc['Reservations'][0]['Instances'][0]['State']['Name']
        
        if state != "stopped":
            return {"result": f"⚠️ 修改失敗：機器目前狀態是 '{state}'。請先呼叫 /stop 讓它關機，才能修改規格。"}
            
        # 2. 執行修改
        client.modify_instance_attribute(
            InstanceId=req.instance_id,
            InstanceType={'Value': req.new_instance_type}
        )
        return {"result": f"✅ 規格已修改為 {req.new_instance_type}，您現在可以重新啟動它了。"}
    except Exception as e: return {"error": str(e)}

# 5. 刪除 (Delete): 終止機器
@app.post("/aws/ec2/terminate", tags=["EC2"], summary="終止 (刪除) EC2")
async def ec2_terminate(req: EC2ActionRequest):
    try:
        ec2 = aws_session.client('ec2')
        ec2.terminate_instances(InstanceIds=[req.instance_id])
        return {"result": f"🗑️ 機器 {req.instance_id} 已開始銷毀程序。"}
    except Exception as e: return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)