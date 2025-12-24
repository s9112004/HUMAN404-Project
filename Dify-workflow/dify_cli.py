#!/usr/bin/env python3
import json
import requests
import sys
import time
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.spinner import Spinner
from rich.live import Live
from rich.table import Table
from rich import box

# ================= 設定區 =================
DIFY_API_KEY = "app-iY6kkDEoOA3es8QjFuElFbii"  # 請確認這是您最新的 API Key
DIFY_BASE_URL = "http://localhost/v1"
USER_ID = "cli-user"
# ===========================================

console = Console()

def print_banner():
    """顯示歡迎畫面"""
    banner_text = """
    [bold cyan]🚀 HUMAN404[/bold cyan]
    [dim]整合 Google 搜尋與 AWS Lambda 資源調度[/dim]
    [yellow]輸入 'exit' 或 'quit' 離開[/yellow]
    """
    console.print(Panel(banner_text, border_style="cyan"))

def send_to_dify(query):
    """傳送指令給 Dify API (Blocking Mode)"""
    url = f"{DIFY_BASE_URL}/workflows/run"
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 根據 AWS_Project_Final.yml，輸入變數為 'command'
    payload = {
        "inputs": {
            "command": query
        },
        "response_mode": "blocking",
        "user": USER_ID,
        "files": []
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        return {"error": "請求超時，Lambda 可能正在冷啟動或執行時間過長。"}
    except requests.exceptions.RequestException as e:
        return {"error": f"連線錯誤: {str(e)}"}

def format_json_output(json_str, title):
    """嘗試解析並美化 JSON 輸出"""
    try:
        if isinstance(json_str, str):
            data = json.loads(json_str)
        else:
            data = json_str
        
        # 情境 A: EC2 列表 {"instances": [...]} 
        if isinstance(data, dict) and "instances" in data:
            table = Table(title="EC2 實例列表", box=box.ROUNDED)
            table.add_column("Name", style="cyan", no_wrap=True)
            table.add_column("Instance ID", style="magenta")
            table.add_column("Type", style="green")
            table.add_column("State", style="bold")
            table.add_column("Public IP", style="yellow")

            for inst in data["instances"]:
                state_style = "green" if inst["State"] == "running" else "red"
                table.add_row(
                    inst.get("Name", "N/A"),
                    inst.get("InstanceId", "N/A"),
                    inst.get("InstanceType", "N/A"),
                    f"[{state_style}]{inst.get('State', 'N/A')}[/{state_style}]",
                    inst.get("PublicIp", "N/A")
                )
            console.print(table)
            return

        # 情境 B: S3 Buckets {"buckets": [...]} 
        if isinstance(data, dict) and "buckets" in data:
            result_text = "[bold yellow]🪣 S3 Buckets[/bold yellow]\n"
            for b in data["buckets"]:
                result_text += f"• {b}\n"
            console.print(Panel(result_text, border_style="yellow"))
            return

        # 情境 C: S3 Files {"files": [...]} 
        if isinstance(data, dict) and "files" in data:
            result_text = "[bold yellow]📄 S3 檔案列表[/bold yellow]\n"
            if not data["files"]:
                result_text += "[dim](Bucket 為空)[/dim]"
            for f in data["files"]:
                result_text += f"• {f}\n"
            console.print(Panel(result_text, border_style="yellow"))
            return

        # 情境 D: 操作結果 (Start/Stop)
        # 通常格式: {"message": "...", "status": "..."}
        # 或者可能是 list [{"message":...}]
        items = data if isinstance(data, list) else [data]
        if items and isinstance(items[0], dict) and "message" in items[0]:
            result_text = "[bold green]⚙️ 操作執行報告[/bold green]\n"
            for item in items:
                status = item.get('status', 'unknown')
                msg = item.get('message', '')
                color = "green" if status in ['pending', 'running', 'stopping', 'stopped'] else "red"
                result_text += f"• {msg} (Status: [{color}]{status}[/{color}])\n"
            console.print(Panel(result_text, border_style="green"))
            return

        # 其他 JSON
        console.print(Panel(json.dumps(data, indent=2, ensure_ascii=False), title=title, border_style="blue"))

    except Exception:
        # 解析失敗，直接印文字
        console.print(Panel(str(json_str), title=title, border_style="blue"))

def format_output(data):
    """根據 Workflow 輸出來決定顯示方式"""
    if "error" in data:
        console.print(Panel(f"[bold red]❌ 執行錯誤[/bold red]\n{data['error']}", border_style="red"))
        return

    workflow_status = data.get("data", {}).get("status")
    
    if workflow_status == "succeeded":
        outputs = data.get("data", {}).get("outputs", {})
        
        # 根據 AWS_Project_Final.yml 的輸出變數進行判斷
        
        # 1. Google 搜尋結果
        if outputs.get("google_result"):
            console.print(Panel(Markdown(outputs["google_result"]), title="🔍 Google 搜尋結果", border_style="green"))
            return

        # 2. EC2 列表結果
        if outputs.get("ec2_list_result"):
            format_json_output(outputs["ec2_list_result"], "EC2 列表")
            return

        # 3. 啟動 EC2 結果
        if outputs.get("start_ec2_result"):
            format_json_output(outputs["start_ec2_result"], "啟動結果")
            return

        # 4. 停止 EC2 結果
        if outputs.get("stop_ec2_result"):
            format_json_output(outputs["stop_ec2_result"], "停止結果")
            return

        # 5. S3 結果
        if outputs.get("s3_result"):
            format_json_output(outputs["s3_result"], "S3 結果")
            return

        # 6. 如果都沒有 (可能是未知意圖)
        console.print(Panel("[yellow]⚠️ 執行完成，但沒有收到預期的輸出。請確認您的指令是否清晰。[/yellow]", border_style="yellow"))
        # Debug: 印出所有 outputs 以便除錯
        console.print("[dim]Raw Outputs:[/dim]")
        console.print(outputs)

    else:
        error_msg = data.get("data", {}).get("error", "未知錯誤")
        console.print(Panel(f"[bold red]❌ 任務失敗[/bold red]\n原因: {error_msg}", border_style="red"))

def main():
    print_banner()
    
    while True:
        try:
            user_input = Prompt.ask("\n[bold cyan]請輸入指令[/bold cyan]")
            
            if user_input.strip().lower() in ['exit', 'quit']:
                console.print("[yellow]👋 再見！[/yellow]")
                break
            
            if not user_input.strip():
                continue

            with Live(Spinner("dots", text="[cyan]AI 正在思考與調度...[/cyan]", style="cyan"), refresh_per_second=10, transient=True):
                result = send_to_dify(user_input)
            
            format_output(result)

        except KeyboardInterrupt:
            console.print("\n[yellow]👋 強制結束[/yellow]")
            break

if __name__ == "__main__":
    main()