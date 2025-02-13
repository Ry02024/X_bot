import os
import random
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

# トピックリスト
TOPICS = [
    "食生活の工夫 - 厚めの鶏ハムやチゲ丼など、健康的かつ簡単に作れるレシピ。",
    "時間管理とリフレッシュ方法 - 忙しいスケジュールの中で効率よく休む方法やストレス解消の工夫。",
    "趣味の探索 - 新しい趣味やスキル（例えば絵画、陶芸、音楽など）に挑戦する方法。",
    "心地よい生活空間作り - ミニマリズムや片付けの工夫で、居心地の良い部屋を作るヒント。",
    "運動と健康管理 - 日常生活に取り入れられる軽い運動や健康的な生活習慣。",
    "言語学習の工夫 - 効率的な英語学習法や、実生活に役立つフレーズの習得。",
    "テクノロジーを活用した生活の最適化 - 家事やスケジュール管理に役立つアプリやツールの活用法。",
    "自己成長のための読書 - 日々の生活やキャリアにインスピレーションを与える書籍の選び方。",
    "家族や友人との時間の過ごし方 - 大切な人ともっと充実した時間を過ごすためのアイデア。",
    "季節ごとの楽しみ方 - 季節に合わせた旅行プランや、趣味（花見、紅葉狩り、雪景色の楽しみ方）。"
]

# トピックをランダムに選択
def select_random_topic():
    return random.choice(TOPICS)

# 選択されたトピックに基づいて記事を生成
def generate_article(topic):
    prompt = f"""
    以下のトピックについて、100字程度で簡潔かつ具体的に丁寧語（です・ます調）で説明してください。
    トピック: {topic}
    """
    gov_topic = """
    あなたは、中立的な立場で政治について解説するAIです。以下の点に注意して、Twitterで発言してください。

    * 事実に基づいた情報を提供してください。
    * 客観的な視点を維持してください。
    * 感情的な表現や攻撃的な表現は避けてください。
    * 人種、宗教、性別、性的指向、障害など、特定の属性を持つ人々に対する差別的な表現は避けてください。
    * プライバシーを侵害する可能性のある情報や個人を特定できる情報を公開しないでください。
    * 名誉毀損、著作権侵害、選挙運動規制など、法律に違反する可能性のある発言はしないでください。
    * 議論を活性化するように努めてください。
    * あなたがAIであることを明記してください。
    
    今日のテーマは、金融所得課税の引き上げについてです。
    上記に基づいて、金融所得課税の引き上げに関するメリットとデメリットを客観的に解説してください。
    100字程度で簡潔かつ具体的に丁寧語（です・ます調）で説明してください。
    """
    try:
        response = genai.GenerativeModel(model_name="gemini-1.5-pro").generate_content(contents=[gov_topic])
        generated_text = response.text.strip() if response.text else "記事を生成できませんでした。"
        return generated_text
    except Exception as e:
        raise Exception(f"Gemini APIエラー: {e}")

# 140字に切り詰める
def trim_to_140_chars(text):
    return text[:140]

# Xに投稿する
def post_to_x(text):
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
        # トピックをランダムに選択
        topic = select_random_topic()
        print(f"選択されたトピック: {topic}")

        # 記事を生成
        article = generate_article(topic)
        print(f"生成された記事: {article}")

        # 140字に切り詰める
        tweet_content = trim_to_140_chars(article)
        print(f"投稿する文章（140字以内）: {tweet_content}")

        # Xに投稿
        post_to_x(tweet_content)

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
