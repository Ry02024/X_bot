import requests
import os

# 環境変数からトークンを取得
API_KEY = os.getenv("X_API_KEY")
API_SECRET = os.getenv("X_API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

# ヘッダー設定
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
}

# 投稿内容
tweet_content = "This is a test tweet from the updated system!"

# X API v2の投稿エンドポイントを使用
def post_tweet(content):
    url = "https://api.twitter.com/2/tweets"
    payload = {"text": content}
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 201:
        print("Tweet posted successfully!")
    else:
        print(f"Error posting to X: {response.status_code} - {response.text}")

if __name__ == "__main__":
    post_tweet(tweet_content)
