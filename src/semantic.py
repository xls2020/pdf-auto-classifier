import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def get_similarity_matrix(vectors):
    """
    计算向量集合的余弦相似度矩阵，用于语义分析。
    """
    return cosine_similarity(vectors)
