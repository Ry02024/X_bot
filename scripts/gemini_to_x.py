import requests
import os

# 環境変数からBearer Tokenを取得
BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")

# ヘッダーの設定
headers = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json"
}

# 投稿内容
def post_to_x(content):
    url = "https://api.twitter.com/2/tweets"
    payload = {"text": content}

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 201:
        print("Tweet posted successfully!")
    else:
        print(f"Error posting to X: {response.status_code} - {response.json()}")

if __name__ == "__main__":
    tweet_content = "This is a test tweet using OAuth 2.0 User Context and X_BEARER_TOKEN!"
    post_to_x(tweet_content)
