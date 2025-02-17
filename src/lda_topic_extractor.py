from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import re

def extract_topic_keywords(texts, top_n=5, max_features=1000, random_state=42):
    """
    对一组文本集合进行 LDA 分析，返回主题中权重最高的 top_n 个关键词，
    并生成一个适合作为目录名称的字符串。
    """
    if not texts:
        return "unknown"
    
    vectorizer = TfidfVectorizer(stop_words="english", max_features=max_features)
    X = vectorizer.fit_transform(texts)
    lda = LatentDirichletAllocation(n_components=1, random_state=random_state)
    lda.fit(X)
    
    feature_names = vectorizer.get_feature_names_out()
    topic = lda.components_[0]
    top_indices = topic.argsort()[-top_n:][::-1]
    top_words = [feature_names[i] for i in top_indices]
    
    # 组合生成目录名称，并清理非法字符
    dir_name = "_".join(top_words)
    dir_name = re.sub(r'\W+', '_', dir_name).lower()
    return dir_name
