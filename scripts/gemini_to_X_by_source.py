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

# 2. データフォルダ内の全てのDOCXファイルを読み込む
def read_all_docx_in_folder(folder_path="data"):
    all_text = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".docx"):  # DOCXファイルのみ対象
            file_path = os.path.join(folder_path, file_name)
            print(f"📂 読み込み中: {file_path}")
            text = read_docx(file_path)
            all_text.append(text)
    return "\n".join(all_text)

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
    prompt = f"""以下の関連情報を要約してください。いくつか重要なトピックスが出来ると思いますが、その中から一つ選んで、そのエッセンスを丁寧語で100字前後の短文として生成してください。
    * 自分の知識を既知にすることや、問いかけの表現をやめてください。
    * インタビューやアンケートについての調査に関する言及もやめてください。
    関連情報:
    {context}
    """
    try:
        response = genai.GenerativeModel(model_name="gemini-1.5-pro").generate_content(contents=[prompt])
        tweet = trim_to_140_chars(response)
        return tweet
    except Exception as e:
        return f"Gemini APIエラー: {e}"

# 🔹 140字以内に「。」（句点）で収める関数
def trim_to_140_chars(text):
    if len(text) <= 140:
        return text  # すでに140字以内ならそのまま返す

    # 「。」で区切る（140字以内の最も後ろの「。」を探す）
    last_period = text[:140].rfind("。")
    if last_period != -1:
        return text[:last_period + 1]  # 「。」を含めて切る

    # もし「。」がなければ、強制的に140字で切る
    return text[:140]

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

if __name__ == "__main__":
    folder_path = "data"  # DOCXファイルが格納されているフォルダ
    text = read_all_docx_in_folder(folder_path)
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
