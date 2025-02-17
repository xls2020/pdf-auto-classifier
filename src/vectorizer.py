from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

def get_document_vectors(doc_texts, method="tfidf"):
    """
    将文档文本转化为向量表示。
    method: "tfidf" 使用TF-IDF；"bert" 使用预训练BERT模型（需安装sentence-transformers）。
    """
    if method == "tfidf":
        vectorizer = TfidfVectorizer(max_features=50000)
        vectors = vectorizer.fit_transform(doc_texts)
        return vectors.toarray()
    elif method == "bert":
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        vectors = model.encode(doc_texts, show_progress_bar=True)
        return np.array(vectors)
    else:
        raise ValueError("未知的向量化方法")
