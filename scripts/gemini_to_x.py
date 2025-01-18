import tweepy
import os

# 環境変数からトークンを取得
API_KEY = os.getenv("X_API_KEY")
API_SECRET = os.getenv("X_API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

# Tweepyの認証設定
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# テスト投稿
def post_to_x(content):
    try:
        api.update_status(content)
        print("Tweet posted successfully!")
    except Exception as e:
        print(f"Error posting to X: {e}")

if __name__ == "__main__":
    test_content = "This is a test tweet from the automated system!"
    post_to_x(test_content)
