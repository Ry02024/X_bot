import os
import requests
from requests_oauthlib import OAuth1
import google.generativeai as genai

# 環境変数からAPIキーとXの認証情報を取得
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
X_API_KEY = os.getenv("X_API_KEY")
X_API_SECRET = os.getenv("X_API_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")

# 必須環境変数の確認
if not all([GEMINI_API_KEY, X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET]):
    raise ValueError("必要な環境変数が設定されていません。")

# Geminiの初期設定
def configure_gemini(api_key):
    genai.configure(api_key=api_key)
    print("Gemini APIの設定が完了しました。")

configure_gemini(GEMINI_API_KEY)

# 文章を生成（100字程度）
def generate_tweet_content(prompt):
    try:
        response = genai.GenerativeModel(model_name="gemini-1.5-pro").generate_content(contents=[prompt])
        generated_text = response.text.strip() if response.text else "AIの投稿を生成できませんでした。"
        return generated_text
    except Exception as e:
        raise Exception(f"Gemini APIエラー: {e}")

# 140字に切り詰める
def trim_to_140_chars(text):
    return text[:140]

# Xに投稿する
def post_to_x(text):
    # OAuth 1.0a認証
    auth = OAuth1(X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET)
    url = "https://api.twitter.com/2/tweets"
    headers = {"Content-Type": "application/json"}
    payload = {"text": text}
    
    response = requests.post(url, auth=auth, headers=headers, json=payload)
    
    if response.status_code != 201:
        raise Exception(f"Xへの投稿に失敗しました: {response.status_code} {response.text}")
    print(f"✅ Xに投稿しました: {text}")

# メイン処理
if __name__ == "__main__":
    try:
        # プロンプトを定義
        prompt = "人工知能の歴史について説明してください。100文字程度で丁寧語（です・ます調）でお願いします。"

        # Gemini APIで文章を生成
        long_message = generate_tweet_content(prompt)
        print(f"生成された文章: {long_message}")

        # 140字に切り詰める
        tweet_content = trim_to_140_chars(long_message)
        print(f"投稿する文章（140字以内）: {tweet_content}")

        # Xに投稿
        post_to_x(tweet_content)

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
