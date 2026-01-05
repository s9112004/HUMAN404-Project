import os
import mimetypes
import base64
import time
import mysql.connector
import uvicorn
import boto3
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Literal
from dotenv import load_dotenv

# 1. 載入環境變數
load_dotenv()

# 2. 初始化 FastAPI
app = FastAPI(title="AI Assistant - AWS Full Stack Manager")

# === AWS 連線設定 ===
# 嘗試讀取 mcp-user 設定，若無則使用預設
try:
    aws_session = boto3.Session(profile_name='ai-mcp-user', region_name='ap-northeast-1')
    print("✅ 成功載入 AWS profile: ai-mcp-user")
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
    keyword: Optional[str] = Field(None, description="搜尋關鍵字，若要列出全部可留空")
    # 設定上限避免查詢筆數無限制
    limit: int = Field(50, ge=1, le=100, description="回傳筆數限制，預設 50 筆")
    sort: Literal["newest", "oldest"] = Field("newest", description="排序方式：'newest' 為最新(預設)，'oldest' 為最舊")
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

class S3Base64UploadRequest(BaseModel):
    bucket_name: str
    file_name: str
    content_base64: str
    content_type: Optional[str] = None


# --- EC2 相關 (新增/修改/刪除) ---
class EC2LaunchRequest(BaseModel):
    instance_type: str = "t2.micro"
    ami_id: str = "ami-0aec5ae807cea9ce0" # Ubuntu 24.04 (us-east-1)
    name: Optional[str] = None

class EC2ActionRequest(BaseModel):
    instance_id: str

class EC2ModifyRequest(BaseModel):
    instance_id: str
    new_instance_type: str # 例如改成 "t3.medium"

class EC2WaitRequest(BaseModel):
    instance_id: str
    target_state: Literal["running", "stopped", "terminated"]

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
        # A. 基礎 SQL
        sql = "SELECT * FROM document_store"
        params = []

        # B. 關鍵字過濾 (如果有填寫)
        if req.keyword and req.keyword.strip():
            sql += " WHERE title LIKE %s OR content LIKE %s"
            params.extend([f"%{req.keyword}%", f"%{req.keyword}%"])
        
        # C. 排序邏輯 (解決最新/最舊問題)
        # 優先使用 created_at 排序，若時間相同則用 id 輔助
        if req.sort == "oldest":
            sql += " ORDER BY created_at ASC, id ASC"
        else:
            # 預設為 newest
            sql += " ORDER BY created_at DESC, id DESC"

        # D. 筆數限制 (解決只列出 10 筆的問題)
        sql += " LIMIT %s"
        params.append(req.limit)

        # 執行查詢
        cursor.execute(sql, tuple(params))
        results = cursor.fetchall()
        
        # E. 結果回傳
        if not results:
            return {"result": "無相關資料"}
            
        # 格式化輸出 (讓 AI 更容易閱讀時間)
        formatted_results = []
        for row in results:
            # 確保 created_at 轉成字串，避免 JSON 序列化錯誤
            created_time = row['created_at'].strftime("%Y-%m-%d %H:%M:%S") if row.get('created_at') else "未知時間"
            formatted_results.append(
                f"[ID: {row['id']}] {row['title']} (時間: {created_time})"
            )
            
        # 回傳原本的 JSON 結構，或者合併後的字串都可以，這裡回傳結構化資料讓 Dify 自己組
        return {
            "count": len(results),
            "data": results, 
            "formatted_list": "\n".join(formatted_results) # 這是給 AI 偷懶直接讀的
        }

    except Exception as e:
        return {"result": f"搜尋發生錯誤: {str(e)}"}
    finally:
        # 一律釋放資料庫資源
        cursor.close()
        conn.close()

@app.post("/db/add", tags=["Database"])
async def add_doc(req: AddRequest):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO document_store (title, content) VALUES (%s, %s)", (req.title, req.content))
        conn.commit()
        return {"result": f"✅ 已新增: {req.title}"}
    except Exception as e:
        # 避免寫入失敗仍留有未結束的交易
        conn.rollback()
        return {"result": f"新增失敗: {str(e)}"}
    finally:
        cursor.close()
        conn.close()

@app.post("/db/update", tags=["Database"])
async def update_doc(req: UpdateRequest):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        updates = []
        params = []
        # 允許空字串作為明確更新值
        if req.title is not None: updates.append("title=%s"); params.append(req.title)
        if req.content is not None: updates.append("content=%s"); params.append(req.content)
        if not updates: return {"result": "無修改內容"}
        params.append(req.id)
        cursor.execute(f"UPDATE document_store SET {','.join(updates)} WHERE id=%s", tuple(params))
        conn.commit()
        return {"result": f"✅ 已更新 ID: {req.id}"}
    except Exception as e:
        # 避免寫入失敗仍留有未結束的交易
        conn.rollback()
        return {"result": f"更新失敗: {str(e)}"}
    finally:
        cursor.close()
        conn.close()

@app.post("/db/delete", tags=["Database"])
async def delete_doc(req: DeleteRequest):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM document_store WHERE id=%s", (req.id,))
        conn.commit()
        return {"result": f"✅ 已刪除 ID: {req.id}"}
    except Exception as e:
        # 避免寫入失敗仍留有未結束的交易
        conn.rollback()
        return {"result": f"刪除失敗: {str(e)}"}
    finally:
        cursor.close()
        conn.close()

# ===========================
#        S3 功能全集
# ===========================

def iter_s3_body(body, chunk_size: int = 1024 * 1024):
    while True:
        chunk = body.read(chunk_size)
        if not chunk:
            break
        yield chunk

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
        # us-east-1 不需要 LocationConstraint，其他區域需指定
        region = aws_session.region_name or "ap-northeast-1"
        if region == "us-east-1":
            s3.create_bucket(Bucket=req.bucket_name)
        else:
            s3.create_bucket(
                Bucket=req.bucket_name,
                CreateBucketConfiguration={"LocationConstraint": region}
            )
        return {"result": f"✅ Bucket '{req.bucket_name}' 建立成功！"}
    except Exception as e: return {"error": str(e)}

# 4. 新增 (Create): multipart 上傳任何檔案
@app.post("/aws/s3/upload_file", tags=["S3"], summary="multipart 上傳檔案")
async def s3_upload_file(
    bucket_name: str = Form(...),
    file: UploadFile = File(...),
    file_name: Optional[str] = Form(None),
):
    try:
        s3 = aws_session.client('s3')
        key = file_name or file.filename
        if not key:
            raise HTTPException(status_code=400, detail="file_name or file.filename is required")
        content_type = file.content_type or mimetypes.guess_type(key)[0]
        extra_args = {"ContentType": content_type} if content_type else None
        if extra_args:
            s3.upload_fileobj(file.file, bucket_name, key, ExtraArgs=extra_args)
        else:
            s3.upload_fileobj(file.file, bucket_name, key)
        return {"result": f"✅ 檔案 '{key}' 已上傳至 '{bucket_name}'。"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        await file.close()

# 4b.  (Create): JSON Base64 
@app.post("/aws/s3/upload_base64", tags=["S3"], summary="JSON Base64 ")
async def s3_upload_base64(req: S3Base64UploadRequest):
    try:
        s3 = aws_session.client('s3')
        content_type = req.content_type or mimetypes.guess_type(req.file_name)[0]
        data = base64.b64decode(req.content_base64)
        extra_args = {"ContentType": content_type} if content_type else None
        if extra_args:
            s3.put_object(Bucket=req.bucket_name, Key=req.file_name, Body=data, **extra_args)
        else:
            s3.put_object(Bucket=req.bucket_name, Key=req.file_name, Body=data)
        return {"result": f"? ?? '{req.file_name}' ???? '{req.bucket_name}'?"}
    except Exception as e:
        return {"error": str(e)}


# 新增這個 API：透過 URL 上傳 
# 5. 刪除 (Delete): 刪除檔案
@app.post("/aws/s3/delete_file", tags=["S3"], summary="刪除 S3 檔案")
async def s3_delete_file(req: S3FileRequest):
    try:
        s3 = aws_session.client('s3')
        s3.delete_object(Bucket=req.bucket_name, Key=req.file_name)
        return {"result": f"🗑️ 檔案 '{req.file_name}' 已刪除。"}
    except Exception as e: return {"error": str(e)}

# 5b. 查找 (Read): 下載檔案
@app.post("/aws/s3/download_file", tags=["S3"], summary="下載 S3 檔案")
async def s3_download_file(req: S3FileRequest):
    try:
        s3 = aws_session.client('s3')
        url = s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": req.bucket_name, "Key": req.file_name},
            ExpiresIn=900,
        )
        return {"url": url, "method": "GET", "bucket": req.bucket_name, "key": req.file_name}
    except Exception as e:
        return {"error": str(e)}

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
        instances = []
        for r in res['Reservations']:
            for i in r['Instances']:
                tags = {t['Key']: t['Value'] for t in i.get('Tags', [])}
                name = tags.get('Name', "無名稱")
                instances.append({
                    "id": i['InstanceId'],
                    "name": name,
                    "state": i['State']['Name'],
                    "type": i['InstanceType'],
                    "public_ip": i.get('PublicIpAddress'),
                    "private_ip": i.get('PrivateIpAddress'),
                    "tags": tags,
                })
        return {"instances": instances}
    except Exception as e: return {"error": str(e)}

# 1b. 查找 (Read): 單一 EC2 詳細資訊
@app.post("/aws/ec2/get", tags=["EC2"], summary="查詢單一 EC2 詳細資訊")
async def ec2_get(req: EC2ActionRequest):
    try:
        ec2 = aws_session.client('ec2')
        res = ec2.describe_instances(InstanceIds=[req.instance_id])
        inst = res['Reservations'][0]['Instances'][0]
        tags = {t['Key']: t['Value'] for t in inst.get('Tags', [])}
        name = tags.get('Name', "無名稱")
        return {
            "id": inst['InstanceId'],
            "name": name,
            "state": inst['State']['Name'],
            "type": inst['InstanceType'],
            "public_ip": inst.get('PublicIpAddress'),
            "private_ip": inst.get('PrivateIpAddress'),
            "tags": tags,
        }
    except Exception as e: return {"error": str(e)}

# 1c. 查找 (Read): 等待狀態完成
@app.post("/aws/ec2/wait_state", tags=["EC2"], summary="等待 EC2 進入指定狀態")
async def ec2_wait_state(req: EC2WaitRequest):
    try:
        ec2 = aws_session.client('ec2')
        waiter_map = {
            "running": "instance_running",
            "stopped": "instance_stopped",
            "terminated": "instance_terminated",
        }
        waiter = ec2.get_waiter(waiter_map[req.target_state])
        waiter.wait(InstanceIds=[req.instance_id])
        return {"result": f"✅ 已進入 {req.target_state}: {req.instance_id}"}
    except Exception as e: return {"error": str(e)}

# 2. 新增 (Create): 啟動新機器
@app.post("/aws/ec2/launch", tags=["EC2"], summary="購買並啟動 EC2")
async def ec2_launch(req: EC2LaunchRequest):
    try:
        ec2 = aws_session.resource('ec2')
        tags = []
        name = req.name or "AI-Created-Server"
        tags.append({"Key": "Name", "Value": name})
        instances = ec2.create_instances(
            ImageId=req.ami_id, MinCount=1, MaxCount=1, InstanceType=req.instance_type,
            TagSpecifications=[{'ResourceType': 'instance','Tags': tags}]
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
    uvicorn.run(app, host="0.0.0.0", port=8001)
