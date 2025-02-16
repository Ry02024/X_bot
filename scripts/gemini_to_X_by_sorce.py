import os
import random
import numpy as np
from docx import Document
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import faiss

# 1. DOCX からのテキスト抽出
def read_docx(file_path):
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)

# 2. テキストをチャンクに分割（ここでは簡単な例）
def split_text(text, max_length=300):
    sentences = text.split('\n')
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if not sentence.strip():
            continue
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
    embeddings = model.encode(chunks)
    return np.array(embeddings)

# 4. FAISS インデックスの作成
def build_faiss_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index

# 蓄積された知識からランダムに数件のチャンクを取得する関数
def get_random_context(chunks: list, num_chunks: int = 2) -> str:
    sampled = random.sample(chunks, min(num_chunks, len(chunks)))
    return "\n".join(sampled)

# RAGの知識を元に適当なツイートを生成する関数
def generate_tweet_with_rag(context: str) -> str:
    prompt = f"""以下の関連情報に基づき、あなたが言いそうなツイートを、丁寧語で100字前後の短文として生成してください。
                また、自分の知識を既知にすることや、問いかけの表現をやめて下さい。
                インタビューやアンケートについての調査に関する言及もやめて下さい。
                関連情報:
                {context}
                """
    try:
        response = genai.GenerativeModel(model_name="gemini-1.5-pro").generate_content(contents=[prompt])
        generated_text = response.text.strip() if response.text else "記事を生成できませんでした。"
        return generated_text
    except Exception as e:
        return f"Gemini APIエラー: {e}"

## 実行コード

from google.colab import userdata
# 環境変数からAPIキーとXの認証情報を取得
GEMINI_API_KEY = userdata.get("Gemini_api")
X_API_KEY = userdata.get("X_API_KEY")
X_API_SECRET = userdata.get("X_API_SECRET")
X_ACCESS_TOKEN = userdata.get("X_ACCESS_TOKEN")
X_ACCESS_TOKEN_SECRET = userdata.get("X_ACCESS_TOKEN_SECRET")

# Geminiの初期設定
def configure_gemini(api_key):
    genai.configure(api_key=api_key)
    print("Gemini APIの設定が完了しました。")

configure_gemini(GEMINI_API_KEY)

# ※ファイルパスは適宜変更してください
file_path = "/content/161217 Ryo 修士論文 (1).docx"
text = read_docx(file_path)
chunks = split_text(text, max_length=300)
print("分割されたチャンク数:", len(chunks))

# SentenceTransformer を利用して埋め込み生成
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = compute_embeddings(chunks, model)

# # FAISS インデックスの構築
# index = build_faiss_index(embeddings)
# print("FAISS インデックス構築完了。")

# 4. ランダムな文脈情報を取得（トピック指定はせず、知識ベースからランダムに取得）
context_text = get_random_context(chunks, num_chunks=2)
print("=== 取得されたランダム文脈情報 ===")
print(context_text)

# 5. 文脈情報を元にGemini APIでツイート文を生成
tweet = generate_tweet_with_rag(context_text)
print("=== 生成されたツイート文 ===")
print(tweet)
