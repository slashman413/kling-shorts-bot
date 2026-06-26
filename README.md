# Kling Shorts Bot 🎬🤖

**每日自動化 YouTube Shorts 生產線**

每天用 Kling AI 生成 10 支爆款 Shorts，自動上傳到你的 YouTube 頻道。

> 🎯 **目標頻道**: https://youtube.com/@GentleSoul666
> 
> ⚡ **每日產能**: 10 支高品質 Shorts 短影片
> 
> 🤖 **全自動**: GitHub Actions 排程 + Kling AI + YouTube API

## 🔥 核心流程

```
逆向工程分析爆款 → AI 生成創意 → Kling AI 生影片 → YouTube 自動上傳
    一次分析           每天10支            AI生成5秒        每日08:00
   (已由 Hermes 完成)   (GPT-4o)          (Kling v3)        (Data API)
```

## 📋 前置準備

你需要註冊以下服務：

| 服務 | 用途 | 費用 |
|------|------|------|
| [Kling AI](https://klingai.com) | 文字→影片生成 | 新用戶有免費額度 |
| [OpenAI](https://platform.openai.com) | AI 創意 Prompt 生成 | ~$0.1/天 |
| [Google Cloud](https://console.cloud.google.com) | YouTube 上傳 | 免費 |

## 🚀 快速開始

**完整設定步驟請看 [setup_guide.md](setup_guide.md)**

1. 註冊 Kling AI + 取得 API Key
2. 註冊 OpenAI + 取得 API Key
3. 設定 Google Cloud → YouTube Data API → OAuth
4. Fork 這個 Repo → 設定 GitHub Secrets
5. 自動開工！🎉

## 🏗️ 專案結構

```
├── .github/workflows/
│   └── daily-shorts.yml     # 每日排程 (UTC 00:00)
├── src/
│   ├── main.py              # Pipeline 主流程
│   ├── kling_client.py      # Kling AI API 封裝
│   ├── prompt_generator.py  # 爆款 Shorts Prompt 生成
│   └── youtube_uploader.py  # YouTube Data API v3 上傳
├── config.yaml              # 設定檔
├── setup_guide.md           # 完整設定指南
└── requirements.txt
```

## 📊 每日排程

| 時間 (台灣) | 步驟 | 說明 |
|------------|------|------|
| 08:00 | 觸發 | GitHub Actions 啟動 |
| 08:01 | 概念生成 | GPT-4o 產生 10 個爆款概念 |
| 08:03 | 影片生成 | Kling AI 逐一生成 5 秒影片 |
| ~09:30 | 上傳 | 自動上傳到 YouTube Shorts |
| 09:31 | 完成 | 輸出日誌 + 通知 |

## ⚙️ GitHub Secrets

| Secret | 說明 |
|--------|------|
| `KLING_ACCESS_KEY` | Kling API Access Key |
| `KLING_SECRET_KEY` | Kling API Secret Key |
| `OPENAI_API_KEY` | OpenAI API Key |
| `YOUTUBE_CLIENT_ID` | Google OAuth Client ID |
| `YOUTUBE_CLIENT_SECRET` | Google OAuth Client Secret |
| `YOUTUBE_REFRESH_TOKEN` | 永久 Refresh Token |

## 🤝 貢獻

歡迎 PR！可以改進的地方：

- 更多爆款 Shorts 分析模板
- 其他 AI 影片引擎支援（Runway/Pika/Sora）
- YouTube 頻道分析 & 優化建議
