# keyword_validator.py
"""
用于在处理完所有文献后检查每个文献的关键词列表是否“有意义”。如果某个文献的关键词中
大部分都不在常用英文词汇中（例如使用 NLTK 的 words 词库进行校验），则认为这些关键词无意义，
并将该文献的路径保存到一个单独的文件中，以便后续手动调整。

"""

# import nltk
from nltk.corpus import words

# 确保停用词和词库已下载
# nltk.download('words', quiet=True)

# 建立一个英文词汇集合（全部转换为小写）
english_vocab = set(w.lower() for w in words.words())

def is_meaningful(word):
    """
    判断单词是否为有意义的英文单词。
    可以根据需要进一步调整，比如对长度做限制（短词一般无意义）。
    """
    if len(word) < 3:  # 太短的词认为无意义
        return False
    return word.lower() in english_vocab
