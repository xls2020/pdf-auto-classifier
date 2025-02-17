# src/zotero_uploader.py
import os
import yaml
from pathlib import Path
from pyzotero import zotero
import argparse

def load_zotero_config(config_file):
    """
    加载 Zotero 配置文件（包含 library_id, library_type, api_key）
    """
    with open(config_file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def upload_pdf_to_zotero(zot, pdf_path, tags):
    """
    上传单个 PDF 文件到 Zotero，并为其添加标签
    :param zot: 已初始化的 Zotero 对象
    :param pdf_path: PDF 文件的完整路径（Path 对象）
    :param tags: 标签列表（从文件所在目录结构中提取）
    """
    title = pdf_path.stem  # 使用文件名作为标题
    # 构造附件条目，注意：Zotero 的附件条目需要 linkMode 设置为 "imported_file"
    item = {
        "itemType": "attachment",
        "title": title,
        "tags": [{"tag": t} for t in tags],
        "contentType": "application/pdf",
        "linkMode": "imported_file",
        "filename": pdf_path.name
    }
    
    # 创建条目
    try:
        created = zot.create_items([item])
        # 从返回信息中提取新建条目的 key
        created_key = list(created['successful'].values())[0]['key']
    except Exception as e:
        print(f"Error creating item for {pdf_path}: {e}")
        return

    # 上传附件文件到刚创建的条目中
    try:
        zot.attach_file(created_key, pdf_file_path=str(pdf_path))
        print(f"Uploaded {pdf_path} to Zotero with tags: {tags}")
    except Exception as e:
        print(f"Error uploading file {pdf_path}: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/zotero_config.yml", help="Zotero配置文件路径")
    parser.add_argument("--input", default="data/classified", help="分类后的PDF所在目录")
    args = parser.parse_args()

    # 加载 Zotero 配置
    config = load_zotero_config(args.config)
    library_id = config.get("library_id")
    library_type = config.get("library_type", "user")
    api_key = config.get("api_key")
    if not (library_id and api_key):
        print("请在配置文件中设置 library_id 和 api_key")
        return

    # 初始化 Zotero 对象
    zot = zotero.Zotero(library_id, library_type, api_key)

    # 扫描分类后的PDF文件（递归遍历整个目录）
    classified_dir = Path(args.input)
    pdf_files = list(classified_dir.rglob("*.pdf"))
    if not pdf_files:
        print(f"未在 {classified_dir} 中找到PDF文件！")
        return

    for pdf_file in pdf_files:
        # 根据 PDF 文件的相对路径（相对于 classified 目录）提取标签
        # 如： data/classified/cluster_2/subcategory_A/filename.pdf
        # 标签将为： ["cluster_2", "subcategory_A"]
        try:
            relative = pdf_file.relative_to(classified_dir)
            tags = list(relative.parts[:-1])  # 排除文件名部分
        except Exception as e:
            print(f"处理路径 {pdf_file} 出错：{e}")
            continue

        upload_pdf_to_zotero(zot, pdf_file, tags)

if __name__ == "__main__":
    main()
