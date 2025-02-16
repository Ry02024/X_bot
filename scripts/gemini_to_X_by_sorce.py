import os
import random
import numpy as np
from docx import Document
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import faiss
import requests
from requests_oauthlib import OAuth1

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

# 1. DOCX からのテキスト抽出
def read_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

# 2. テキストをチャンクに分割
def split_text(text, max_length=300):
    sentences = text.split('\n')
    chunks, current_chunk = [], ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_length:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

# 3. 埋め込み生成
def compute_embeddings(chunks, model):
    return np.array(model.encode(chunks))

# 4. FAISS インデックス作成
def build_faiss_index(embeddings):
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return index

# 5. ランダムな文脈情報を取得
def get_random_context(chunks, num_chunks=2):
    return "\n".join(random.sample(chunks, min(num_chunks, len(chunks))))

# 6. Gemini API を利用してツイートを生成
def generate_tweet_with_rag(context):
    prompt = f"""以下の関連情報に基づき、あなたが言いそうなツイートを、丁寧語で100字前後の短文として生成してください。
    * 自分の知識を既知にすることや、問いかけの表現をやめてください。
    * インタビューやアンケートについての調査に関する言及もやめてください。
    関連情報:
    {context}
    """
    try:
        response = genai.GenerativeModel(model_name="gemini-1.5-pro").generate_content(contents=[prompt])
        return response.text.strip()[:140] if response.text else "ツイート生成に失敗しました。"
    except Exception as e:
        return f"Gemini APIエラー: {e}"

# 7. X に投稿
def post_to_x(text):
    auth = OAuth1(X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET)
    url = "https://api.twitter.com/2/tweets"
    headers = {"Content-Type": "application/json"}
    payload = {"text": text}

    response = requests.post(url, auth=auth, headers=headers, json=payload)
    if response.status_code != 201:
        raise Exception(f"Xへの投稿に失敗しました: {response.status_code} {response.text}")

    print(f"✅ Xに投稿しました: {text}")

# 実行
if __name__ == "__main__":
    file_path = "data/161217 Ryo 修士論文 (1).docx"  # DOCXファイルのパス
    text = read_docx(file_path)
    chunks = split_text(text)
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = compute_embeddings(chunks, model)
    # index = build_faiss_index(embeddings)

    # ランダムな文脈情報を取得し保存
    context = get_random_context(chunks)
    print("=== 取得されたランダム文脈情報 ===")
    print(context)

    # 文脈を元にツイートを生成
    tweet = generate_tweet_with_rag(context)
    print("=== 生成されたツイート文 ===")
    print(tweet)

    # Xに投稿
    post_to_x(tweet)
