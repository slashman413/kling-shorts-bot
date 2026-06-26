"""
取得 YouTube OAuth Refresh Token - 手動版
支援分段執行
"""
import json, os, pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
STATE_FILE = "oauth_code_verifier.txt"

# 檢查是否有存檔
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        saved = json.load(f)
    
    code = input("👉 請貼上授權碼: ").strip()
    
    # 重新建立 flow 並注入 code_verifier
    flow = InstalledAppFlow.from_client_secrets_file(
        "client_secret.json",
        scopes=SCOPES,
        redirect_uri="urn:ietf:wg:oauth:2.0:oob",
    )
    # 注入 code_verifier
    flow.oauth2session._client.code_verifier = saved["code_verifier"]
    
    flow.fetch_token(code=code)
    creds = flow.credentials
    
    os.remove(STATE_FILE)
    
    print()
    print("=" * 60)
    print("  ✅ OAuth 認證成功！")
    print("=" * 60)
    print()
    print("📌 YOUTUBE_REFRESH_TOKEN ⭐")
    print(creds.refresh_token)
    print()
    # Also save to file
    with open("refresh_token.txt", "w") as f:
        f.write(creds.refresh_token)
    print("(已同時儲存到 refresh_token.txt)")
else:
    flow = InstalledAppFlow.from_client_secrets_file(
        "client_secret.json",
        scopes=SCOPES,
        redirect_uri="urn:ietf:wg:oauth:2.0:oob",
    )
    
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    
    # 儲存 code_verifier
    code_verifier = flow.oauth2session._client.code_verifier
    with open(STATE_FILE, "w") as f:
        json.dump({"code_verifier": code_verifier}, f)
    
    print("\n" + "=" * 70)
    print("  🔗 在你的瀏覽器中打開這個網址：")
    print("=" * 70)
    print()
    print(auth_url)
    print()
    print("=" * 70)
    print("  步驟:")
    print("  1. 登入你的 Google 帳號")
    print("  2. 點「Continue」允許授權")
    print("  3. 複製出現的授權碼")
    print("  4. 再執行一次: python get_refresh_token.py")
    print("  5. 貼上授權碼")
    print("=" * 70)
