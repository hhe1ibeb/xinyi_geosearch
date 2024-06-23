from sentence_transformers import SentenceTransformer

# https://huggingface.co/thenlper/gte-large
embedding_model_en = SentenceTransformer("thenlper/gte-large")
embedding_model_zh = SentenceTransformer("thenlper/gte-large-zh")


def get_embedding(text: str, lang: str) -> list[float]:
    if not text.strip():
        print("Attempted to get embedding for empty text.")
        return []
    if lang == "zh": embedding = embedding_model_zh.encode(text)
    else: embedding = embedding_model_en.encode(text)

    return embedding.tolist()