import numpy as np 
import matplotlib.pyplot as plt
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from sklearn.cluster import AgglomerativeClustering

def cluster_documents(vectors, method="hierarchical", max_clusters=10, visualize=True, n_clusters=None):
    """
    对文档向量进行聚类，可以自动选择最佳聚类数目，也可以手动指定聚类数目。
    
    参数:
      vectors: 文档向量数组。
      method: "kmeans" 或 "hierarchical"（层次聚类）。
      max_clusters: 自动选择聚类数时的最大聚类数范围。
      visualize: 是否绘制聚类评估图形（如肘部图或 dendrogram）。
      n_clusters: 手动指定聚类数目。如果传入一个整数，则使用该聚类数；如果为 None，则自动选择最佳聚类数目。
      
    返回:
      labels: 聚类结果标签数组。
    """
    
    if method == "kmeans":
        if n_clusters is None:
            # 自动选择聚类数：使用肘部法则
            sse = []
            for k in range(2, max_clusters + 1):  # 2 到 max_clusters
                model = KMeans(n_clusters=k, random_state=42)
                model.fit(vectors)
                sse.append(model.inertia_)
            
            # 绘制肘部法则图
            if visualize:
                plt.figure(figsize=(8, 6))
                plt.plot(range(2, max_clusters + 1), sse, marker='o')
                plt.title('Elbow Method for KMeans')
                plt.xlabel('Number of Clusters')
                plt.ylabel('SSE')
                plt.show()
            
            # 选择肘部位置的 k 值（这里简单使用 SSE 差值的最大变化点）
            best_k = np.argmax(np.diff(sse)) + 2
            print(f"通过肘部法则自动选择最佳聚类数: {best_k}")
        else:
            best_k = n_clusters
            print(f"使用手动指定的聚类数: {best_k}")
        
        # KMeans 进行聚类
        model = KMeans(n_clusters=best_k, random_state=42)
        labels = model.fit_predict(vectors)

    elif method == "hierarchical":
        # 计算层次聚类所需的链接矩阵
        linked = linkage(vectors, 'ward')

        # 绘制 Dendrogram
        if visualize:
            plt.figure(figsize=(8, 6))
            dendrogram(linked)
            plt.title('Dendrogram for Hierarchical Clustering')
            plt.xlabel('Document Index')
            plt.ylabel('Distance')
            plt.show()
        
        if n_clusters is None:
            # 自动选择最佳聚类数 (使用 silhouette_score)
            best_k = 2
            best_score = -1
            for k in range(2, max_clusters + 1):
                temp_labels = fcluster(linked, k, criterion='maxclust')  # 生成聚类标签
                try:
                    score = silhouette_score(vectors, temp_labels)
                    if score > best_score:
                        best_k = k
                        best_score = score
                except Exception as e:
                    continue
            print(f"自动选择的最佳层次聚类数: {best_k}")
        else:
            best_k = n_clusters
            print(f"使用手动指定的聚类数: {best_k}")
        
        # 最终使用 AgglomerativeClustering 进行聚类
        model = AgglomerativeClustering(n_clusters=best_k, metric='euclidean', linkage='ward')
        labels = model.fit_predict(vectors)
    
    else:
        raise ValueError("未知的聚类方法")
    
    # 计算并输出轮廓系数
    try:
        score = silhouette_score(vectors, labels)
        print(f"聚类方法：{method}, 聚类数: {best_k}, 轮廓系数: {score:.3f}")
    except Exception as e:
        print("计算轮廓系数时出错：", e)
    
    return labels
