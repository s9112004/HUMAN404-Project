#!/bin/bash

# 定義路徑
PROJECT_DIR="/home/hsu/HUMAN404-Project/Dify-workflow"
PACKAGE_DIR="${PROJECT_DIR}/package"
DEPLOY_ZIP="${PROJECT_DIR}/deployment.zip"
HANDLER_FILE="aws_lambda_handler.py"

echo "🚀 開始打包 Lambda 部署檔案..."

# 1. 檢查 package 資料夾
if [ ! -d "$PACKAGE_DIR" ]; then
    echo "❌ 錯誤: 找不到 package 資料夾！請先執行 pip install。"
    exit 1
fi

# 2. 移除舊的 zip
if [ -f "$DEPLOY_ZIP" ]; then
    echo "🗑️  移除舊的 deployment.zip..."
    rm "$DEPLOY_ZIP"
fi

# 3. 壓縮相依套件
echo "📦 正在壓縮相依套件 (這可能需要幾秒鐘)..."
cd "$PACKAGE_DIR"
zip -r -q "$DEPLOY_ZIP" .
if [ $? -ne 0 ]; then
    echo "❌ 壓縮套件失敗！"
    exit 1
fi

# 4. 加入主程式
echo "📄 加入 $HANDLER_FILE..."
cd "$PROJECT_DIR"
zip -g "$DEPLOY_ZIP" "$HANDLER_FILE"
if [ $? -ne 0 ]; then
    echo "❌ 加入主程式失敗！"
    exit 1
fi

echo "✅ 打包完成！"
echo "📂 檔案位置: $DEPLOY_ZIP"
echo "👉 下一步: 請將此檔案上傳至 AWS Lambda Console。"
