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
X_BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")

# 必須環境変数の確認
if not all([GEMINI_API_KEY, X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET]):
    raise ValueError("必要な環境変数が設定されていません。")

# Geminiの初期設定
def configure_gemini(api_key):
    genai.configure(api_key=api_key)
    print("Gemini APIの設定が完了しました。")

configure_gemini(GEMINI_API_KEY)

# Xの過去の投稿を取得
def get_recent_posts(count=2):
    url = "https://api.twitter.com/2/users/me/tweets"
    headers = {
        "Authorization": f"Bearer {X_BEARER_TOKEN}"
    }
    params = {
        "max_results": count
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"Xの投稿取得に失敗しました: {response.status_code} {response.text}")
    
    tweets = response.json().get("data", [])
    return [tweet["text"] for tweet in tweets]

# 新しい話題を生成（過去の話題を除外）
def generate_unique_content(past_topics):
    prompt = f"""
    以下の話題とは異なる新しい話題を生成してください。
    - 過去の話題:
    {', '.join(past_topics)}

    条件:
    - 話題は100字以内で簡潔に記述してください。
    - 内容はユニークで、具体的な情報を含んでください。
    """
    try:
        response = genai.GenerativeModel(model_name="gemini-1.5-pro").generate_content(contents=[prompt])
        generated_text = response.text.strip() if response.text else "新しい投稿を生成できませんでした。"
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
        # 過去2つの投稿を取得
        recent_posts = get_recent_posts(count=2)
        print(f"過去の投稿: {recent_posts}")

        # 新しい話題を生成
        new_content = generate_unique_content(recent_posts)
        print(f"生成された新しい話題: {new_content}")

        # 140字に切り詰める
        tweet_content = trim_to_140_chars(new_content)
        print(f"投稿する文章（140字以内）: {tweet_content}")

        # Xに投稿
        post_to_x(tweet_content)

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
