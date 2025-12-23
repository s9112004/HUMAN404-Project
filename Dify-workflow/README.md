# Dify Guide

## 如何部署
1. 下載「AWS Project.yaml」。
2. 按照 https://docs.google.com/document/d/1eEcGdkNeEF0tVUvDpH3PfqdISnSGjAMVtpfZzbp2lzg/edit?usp=drive_link 的步驟部署本地端Dify。
3. 使用瀏覽器輸入http://YOUR-PC-IP 進入管理員設定頁面，設定帳號密碼後即可登入。
4. 進入「Studio」頁面，點「Import DSL File」，選擇前面下載的「AWS Project.yaml」。即可在頁面中看到這個Workflow。

5. 點最上方的「Tools」，選擇頁面左上「Custom」，並點「Create Custom Tool」。

6. 輸入工具名稱，並將「mcp-tools.json」中的程式碼複製貼上至第二區Schema的區塊。最後按下建立。(這個工具應該不能用，因為目前EC2上的是直接透過內網傳輸，外網若要連接需要詢問Jason)


## 注意事項
1. 若要使用已建立好的MCP工具，需要重新設定已在Workflow中的MCP工具區塊。
2. 大語言模型API需要另外設定。