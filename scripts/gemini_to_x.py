import requests
from requests_oauthlib import OAuth1
import os

def post_to_x(text):
    """
    Xに投稿する関数

    Args:
      text: 投稿するテキスト
    """
    consumer_key = os.environ.get("X_API_KEY")
    consumer_secret = os.environ.get("X_API_SECRET")
    access_token = os.environ.get("X_ACCESS_TOKEN")
    access_token_secret = os.environ.get("X_ACCESS_TOKEN_SECRET")

    if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
        raise ValueError("必要な環境変数が設定されていません。")

    auth = OAuth1(consumer_key, consumer_secret, access_token, access_token_secret)
    url = "https://api.twitter.com/2/tweets"
    headers = {"Content-Type": "application/json"}
    data = {"text": text}
    response = requests.post(url, auth=auth, headers=headers, json=data)

    if response.status_code != 201:
        raise Exception(f"Xへの投稿に失敗しました: {response.status_code} {response.text}")

    print("Xに投稿しました。")


if __name__ == "__main__":
    text = "これはGitHub Actionsからのテスト投稿です。OAuth 1.0a"
    post_to_x(text)
