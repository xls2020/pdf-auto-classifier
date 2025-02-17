import re
from collections import Counter
from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))

# 下载停用词（如果尚未下载）
# nltk.download('stopwords', quiet=True)  # 在 pdf_processor.py 中执行了下载
# stop_words = set(stopwords.words('english'))

def extract_keywords(text, method="frequency", top_n=10):
    """
    从文本中抽取关键词。
    method: "frequency" 使用词频统计，后续可扩展其他方法（如 TF-IDF、TextRank、RAKE）。
    """
    if method == "frequency":
        # 使用正则提取单词
        words = re.findall(r'\b\w+\b', text.lower())
        filtered_words = [w for w in words if w not in stop_words and len(w) > 2]
        freq = Counter(filtered_words)
        most_common = freq.most_common(top_n)
        keywords = [word for word, count in most_common]
        return keywords
    else:
        # 可扩展其他关键词抽取方法
        return []
