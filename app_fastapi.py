# app.py
# Day 3：最小可行 LINE Echo Bot（FastAPI 版本）

import os
from typing import Dict, Any
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 讀取環境變數
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")

if not CHANNEL_SECRET or not CHANNEL_ACCESS_TOKEN:
    raise RuntimeError("請設定環境變數 CHANNEL_SECRET / CHANNEL_ACCESS_TOKEN")

# 初始化 LINE Bot
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(CHANNEL_SECRET)

# 建立 FastAPI 應用
app = FastAPI(title="AI 雲端情人 - Day 3 Echo Bot")

@app.get("/healthz")
async def healthz() -> Dict[str, Any]:
    """健康檢查 API，Render 會定期呼叫"""
    return {"ok": True}

@app.post("/callback")
async def callback(request: Request, x_line_signature: str = Header(None)) -> JSONResponse:
    """LINE Webhook 入口，處理文字訊息並原文回覆"""
    if x_line_signature is None:
        raise HTTPException(status_code=400, detail="Missing X-Line-Signature")

    body_text = (await request.body()).decode("utf-8")

    try:
        events = parser.parse(body_text, x_line_signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    for event in events:
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessage):
            try:
                # Echo：回覆使用者輸入的文字
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=event.message.text)
                )
            except Exception as e:
                print(f"[ERROR] reply_message failed: {e}")

    return JSONResponse({"status": "ok"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", 10000)))