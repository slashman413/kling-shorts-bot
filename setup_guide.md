# Kling Shorts Bot 🎬

**自動化 YouTube Shorts 生產線** — 每天用 Kling AI 生成10支爆款 Shorts 並自動上傳到 YouTube。

## 🔧 設定步驟 (Step by Step)

### Step 1: Kling AI 註冊並取得 API Key

1. 前往 https://klingai.com
2. 點擊右上角 **Sign Up** 註冊帳號
3. 註冊後點擊 **API Platform**
4. 點擊 **Create API Key**
5. 複製 **Access Key** 和 **Secret Key**
6. 保存好這兩個值，之後需要放到 GitHub Secrets

> 💰 Kling AI 新用戶通常有免費額度，之後需充值

---

### Step 2: OpenAI API Key（Prompt 生成用）

1. 前往 https://platform.openai.com/api-keys
2. 點擊 **Create new secret key**
3. 複製 API Key（以 `sk-` 開頭）
4. 如果沒有帳號，可以使用其他 LLM（如 Claude、DeepSeek）— 需要修改 `src/prompt_generator.py`

---

### Step 3: YouTube OAuth 設定（最複雜）

這個步驟讓 GitHub Actions 可以自動上傳影片到你的頻道。

#### 3.1 建立 Google Cloud Project

1. 前往 https://console.cloud.google.com/
2. 點擊頂端下拉選單 → **New Project**
3. 取名為 `kling-shorts-bot`
4. 等待 Project 建立完成

#### 3.2 啟用 YouTube Data API v3

1. 在左側選單 → **API & Services** → **Library**
2. 搜尋 **YouTube Data API v3**
3. 點擊 **Enable**

#### 3.3 建立 OAuth 憑證

1. 左側選單 → **API & Services** → **Credentials**
2. 點擊 **Create Credentials** → **OAuth client ID**
3. 如果是第一次使用，需要先設定 **OAuth consent screen**
   - User Type: **External**
   - App name: `Kling Shorts Bot`
   - User support email: 你的 Email
   - Developer contact: 你的 Email
   - 點擊 **Save and Continue**
   - Scopes: 點擊 **Add or Remove Scopes**
   - 搜尋 `youtube.upload` → 選取
   - 點擊 **Update** → **Save and Continue**
   - Test users: 加入你的 Gmail
   - 回到 Credentials 頁面
4. Application type: **Desktop app**
5. Name: `Shorts Uploader`
6. 點擊 **Create**
7. 點擊 **Download JSON** → 保存為 `client_secret.json`

#### 3.4 取得 Refresh Token

在你的電腦上執行以下腳本（**只需要執行一次**）：

```bash
# 安裝套件
pip install google-auth google-auth-oauthlib google-api-python-client

# 執行 OAuth 腳本
python -c "
from google_auth_oauthlib.flow import InstalledAppFlow

flow = InstalledAppFlow.from_client_secrets_file(
    'client_secret.json',
    scopes=['https://www.googleapis.com/auth/youtube.upload']
)

# 這會打開瀏覽器請你登入 Google
creds = flow.run_local_server(port=8080)

print('REFRESH_TOKEN:', creds.refresh_token)
print('CLIENT_ID:', creds.client_id)
print('CLIENT_SECRET:', creds.client_secret)
"
```

瀏覽器會打開，登入你的 Google 帳號（**YouTube 頻道 @GentleSoul666 的帳號**）
點擊 **Continue** 授權
回到 terminal 會看到三個值：`REFRESH_TOKEN`、`CLIENT_ID`、`CLIENT_SECRET`

---

### Step 4: GitHub 設定

#### 4.1 建立 Repository

```bash
# 在你的 GitHub 上建立新 repo: kling-shorts-bot

# 然後在你的電腦執行：
cd C:\Users\Wayne\kling-shorts-bot
git init
git add .
git commit -m "init: kling shorts bot automated pipeline"
git branch -M main
git remote add origin https://github.com/slashman413/kling-shorts-bot.git
git push -u origin main
```

#### 4.2 設定 GitHub Secrets

前往你的 GitHub Repo → **Settings** → **Secrets and variables** → **Actions**

新增以下 **Repository secrets**：

| Secret Name | Value |
|---|---|
| `KLING_ACCESS_KEY` | 你從 Kling AI 取得的 Access Key |
| `KLING_SECRET_KEY` | 你從 Kling AI 取得的 Secret Key |
| `OPENAI_API_KEY` | 你從 OpenAI 取得的 API Key |
| `YOUTUBE_CLIENT_ID` | 從 OAuth 腳本輸出的 CLIENT_ID |
| `YOUTUBE_CLIENT_SECRET` | 從 OAuth 腳本輸出的 CLIENT_SECRET |
| `YOUTUBE_REFRESH_TOKEN` | 從 OAuth 腳本輸出的 REFRESH_TOKEN |

---

### Step 5: 測試！

1. 前往你的 GitHub Repo → **Actions**
2. 點擊 **每日 Shorts 自動生產線**
3. 點擊 **Run workflow** → **Run workflow**（手動測試）
4. 觀察 Workflow 執行狀況

成功後，GitHub Actions 就會：
- 每天 UTC 00:00（台灣時間早上8:00）自動執行
- 生成 10 個 Shorts 概念
- 用 Kling AI 產生影片
- 上傳到 https://youtube.com/@GentleSoul666

---

## 🏗️ 專案架構

```
kling-shorts-bot/
├── .github/workflows/
│   └── daily-shorts.yml     # GitHub Actions 排程
├── src/
│   ├── main.py              # 主流程編排
│   ├── kling_client.py      # Kling AI API 客戶端
│   ├── prompt_generator.py  # AI Prompt 生成器
│   └── youtube_uploader.py  # YouTube 上傳器
├── output/                  # 每日輸出（自動生成）
├── config.yaml              # 設定檔
├── requirements.txt         # Python 套件
└── setup_guide.md           # 本文件
```

## 🚀 完整流程

```
每天 08:00 (台灣時間)
    │
    ├─ Step 1: GPT-4o 生成 10 個爆款 Shorts 概念
    │   └─ 使用原始分析的心理鉤子 + 變體
    │
    ├─ Step 2: Kling AI 生成短影片 (5秒 each)
    │   └─ 直式 9:16, 破壞/治癒/壓縮風格
    │
    └─ Step 3: YouTube Data API v3 上傳
        └─ 設定 #Shorts 標籤、公開
```

## ⚠️ 注意事項

1. **Kling AI 費用**: 每支影片需要消耗額度，10支/天需要評估預算
2. **YouTube 限制**: 新頻道每天上傳限制較低，建議先從 3-5 支/天開始
3. **版權音樂**: 目前不會自動加音樂，YouTube 會自動提供音樂庫選項
4. **內容審查**: AI 生成的破壞影片可能被標記，注意拿捏暴力程度
