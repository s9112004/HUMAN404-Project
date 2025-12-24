from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from mangum import Mangum
import boto3
from botocore.exceptions import ClientError
from typing import List, Optional
import json

app = FastAPI(title="AWS Resource Manager", version="2.0.0")

# --- Pydantic Models (定義請求格式) ---
class EC2ActionRequest(BaseModel):
    instance_id: str
    region: str = "ap-northeast-1"

class S3ListRequest(BaseModel):
    bucket_name: str

# --- AWS Clients ---
def get_ec2_client(region: str):
    return boto3.client("ec2", region_name=region)

def get_s3_client():
    return boto3.client("s3")

# --- Helper Function: Resolve Instance ID by Name ---
def resolve_instance_id(ec2_client, identifier: str) -> str:
    """
    如果 identifier 是以 i- 開頭，直接回傳。
    否則視為 Name Tag，去搜尋對應的 Instance ID。
    """
    if identifier.startswith("i-"):
        return identifier
    
    # 搜尋 Name Tag
    try:
        response = ec2_client.describe_instances(
            Filters=[
                {'Name': 'tag:Name', 'Values': [identifier]},
                {'Name': 'instance-state-name', 'Values': ['pending', 'running', 'stopping', 'stopped']} # 只找存在的機器
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search instances: {str(e)}")

    instances = []
    for r in response.get('Reservations', []):
        for i in r.get('Instances', []):
            instances.append(i['InstanceId'])
    
    if not instances:
        raise HTTPException(status_code=404, detail=f"No EC2 instance found with name '{identifier}'")
    
    if len(instances) > 1:
        raise HTTPException(status_code=400, detail=f"Multiple instances found with name '{identifier}': {instances}. Please specify ID.")
    
    return instances[0]

# --- EC2 Endpoints ---

@app.get("/aws/ec2/list", summary="列出所有 EC2 實例狀態")
def list_ec2_instances(region: str = "ap-northeast-1"):
    try:
        ec2 = get_ec2_client(region)
        response = ec2.describe_instances()
        instances = []
        for reservation in response.get("Reservations", []):
            for instance in reservation.get("Instances", []):
                name = "Unknown"
                if "Tags" in instance:
                    for tag in instance["Tags"]:
                        if tag["Key"] == "Name":
                            name = tag["Value"]
                
                instances.append({
                    "InstanceId": instance["InstanceId"],
                    "InstanceType": instance["InstanceType"],
                    "State": instance["State"]["Name"],
                    "Name": name,
                    "PublicIp": instance.get("PublicIpAddress", "N/A")
                })
        return {"instances": instances}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/aws/ec2/start", summary="啟動 EC2 實例 (支援 ID 或 Name)")
def start_ec2_instance(request: EC2ActionRequest):
    if not request.instance_id:
        raise HTTPException(status_code=400, detail="Instance ID or Name is required.")

    try:
        ec2 = get_ec2_client(request.region)
        # 解析 ID (支援 Name -> ID)
        real_id = resolve_instance_id(ec2, request.instance_id)
        
        ec2.start_instances(InstanceIds=[real_id])
        return {"message": f"Starting instance {real_id} (Name: {request.instance_id})", "status": "pending"}
    
    except HTTPException as he:
        raise he
    except ClientError as e:
        raise HTTPException(status_code=400, detail=f"AWS Error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/aws/ec2/stop", summary="停止 EC2 實例 (支援 ID 或 Name)")
def stop_ec2_instance(request: EC2ActionRequest):
    if not request.instance_id:
        raise HTTPException(status_code=400, detail="Instance ID or Name is required.")

    try:
        ec2 = get_ec2_client(request.region)
        # 解析 ID (支援 Name -> ID)
        real_id = resolve_instance_id(ec2, request.instance_id)

        ec2.stop_instances(InstanceIds=[real_id])
        return {"message": f"Stopping instance {real_id} (Name: {request.instance_id})", "status": "stopping"}
    
    except HTTPException as he:
        raise he
    except ClientError as e:
        raise HTTPException(status_code=400, detail=f"AWS Error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- S3 Endpoints ---

@app.get("/aws/s3/buckets", summary="列出所有 S3 Buckets")
def list_s3_buckets():
    try:
        s3 = get_s3_client()
        response = s3.list_buckets()
        buckets = [bucket["Name"] for bucket in response.get("Buckets", [])]
        return {"buckets": buckets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/aws/s3/files", summary="列出 Bucket 內的檔案")
def list_s3_files(request: S3ListRequest):
    if not request.bucket_name:
        raise HTTPException(status_code=400, detail="Bucket name is required.")

    try:
        s3 = get_s3_client()
        response = s3.list_objects_v2(Bucket=request.bucket_name)
        files = []
        if "Contents" in response:
            files = [obj["Key"] for obj in response["Contents"]]
        return {"files": files}
        
    except ClientError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", summary="Health Check")
def root():
    return {"message": "AWS Resource Manager v2 is running!"}

# --- Lambda Adapter ---
handler = Mangum(app)
