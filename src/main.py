import argparse
import os
import shutil
import json
import nltk
from pathlib import Path
from tqdm import tqdm
import yaml
import re
import numpy as np
from pdf_processor import extract_metadata
from keyword_extractor import extract_keywords
from vectorizer import get_document_vectors
from clustering import cluster_documents
from lda_topic_extractor import extract_topic_keywords
from keyword_validator import is_meaningful

def load_config(config_path="config/config.yml"):
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="PDF输入目录")
    parser.add_argument("--output", default="data/classified", help="分类输出目录")
    parser.add_argument("--config", default="config/config.yml", help="配置文件路径")
    args = parser.parse_args()

    # 加载配置
    config = load_config(args.config)
    matching_config = config.get("matching", {})
    vector_method = matching_config.get("vector_method", "tfidf")
    clustering_method = matching_config.get("clustering_method", "hierarchical")
    num_clusters = matching_config.get("num_clusters", 10)
    n_clusters = matching_config.get("n_clusters", 10)
    visualize = matching_config.get("visualize", False)
    top_n_keywords = matching_config.get("top_n_keywords", 10)
    topic_n_keywords = matching_config.get("topic_n_keywords", 5)
    threshold = matching_config.get("threshold", 1)  # 目前未直接使用，可扩展

    # 处理 NLTK 配置
    nltk_path = config.get("nltk", {}).get("nltk_path", "nltk_data")  # 获取 NLTK 数据路径
    nltk_download = config.get("nltk", {}).get("nltk_download", True)  # 获取是否下载资源

    # 设置 NLTK 数据存储路径
    os.environ["NLTK_DATA"] = nltk_path

    # 如果需要下载 NLTK 数据
    if nltk_download:             
        nltk.download('words', download_dir=nltk_path, quiet=True)
        nltk.download('stopwords', download_dir=nltk_path, quiet=True)
    # print(nltk.data.path)
    # print(nltk.data.find('corpora/stopwords'))
    # print(nltk.data.find('corpora/words'))

    # 准备输出目录
    output_dir = Path(args.output)
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 读取PDF文件
    pdf_dir = Path(args.input)
    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        print("未找到PDF文件！")
        return

    documents = []
    metadata_list = []
    for pdf_path in tqdm(pdf_files, desc="提取PDF文本"):
        meta = extract_metadata(str(pdf_path))
        if meta:
            meta["keywords"] = extract_keywords(meta["content"], method="frequency", top_n=top_n_keywords)
            documents.append(meta["content"])
            metadata_list.append(meta)

    # 获取文档向量
    vectors = get_document_vectors(documents, method=vector_method)
    
    # 聚类
    labels = cluster_documents(vectors, method=clustering_method, max_clusters=num_clusters, visualize=True, n_clusters=n_clusters)

    # 生成目录名称
    cluster_texts = {}
    for i, label in enumerate(labels):
        cluster_texts.setdefault(label, []).append(documents[i])
    
    cluster_names = {}
    for label, texts in cluster_texts.items():
        name = extract_topic_keywords(texts, top_n=topic_n_keywords)
        cluster_names[label] = f"{name}_{label}"
        print(f"聚类 {label} 目录名称： {cluster_names[label]}")
    
    # 组织文件到对应聚类目录
    results = []
    for meta, label in zip(metadata_list, labels):
        cluster_dir = output_dir / cluster_names[label]
        cluster_dir.mkdir(parents=True, exist_ok=True)
        src_path = Path(meta["path"])
        dest_path = cluster_dir / src_path.name
        try:
            shutil.copy(str(src_path), str(dest_path))
        except Exception as e:
            print(f"文件移动失败: {src_path} -> {dest_path} 错误: {e}")
            continue
        results.append({
            "original": str(src_path),
            "new_path": str(dest_path),
            "cluster": int(label),
            "cluster_name": cluster_names[label],
            "keywords": meta.get("keywords", [])
        })
    
    # 保存报告
    report_path = Path("data/logs/report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"分类完成，共处理 {len(results)} 个文件。报告保存在 {report_path}")

    # 保存处理结果
    save_dir = "data/logs/preprocessed"
    os.makedirs(save_dir, exist_ok=True)
    
    with open(os.path.join(save_dir, "documents.json"), "w", encoding="utf-8") as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)
    with open(os.path.join(save_dir, "metadata_list.json"), "w", encoding="utf-8") as f:
        json.dump(metadata_list, f, ensure_ascii=False, indent=2)
    np.save(os.path.join(save_dir, "vectors.npy"), vectors)
    
    # 关键词有效性检查
    problematic_docs = []
    for meta in metadata_list:
        keywords = meta.get("keywords", [])
        if not keywords:
            continue
        meaningless_count = sum(1 for kw in keywords if not is_meaningful(kw))
        if meaningless_count / len(keywords) > 0.5:
            problematic_docs.append(meta["path"])
    
    with open("data/logs/problematic_documents.txt", "w", encoding="utf-8") as f:
        for path in problematic_docs:
            f.write(path + "\n")
    print(f"发现 {len(problematic_docs)} 个文献关键词问题，请检查 data/logs/problematic_documents.txt")

if __name__ == "__main__":
    main()
