# pdf_processor.py
import pdfplumber
from pathlib import Path
from text_cleaner import clean_extracted_text  # 导入文本清洗模块

def extract_metadata(pdf_path):
    """
    从 PDF 文件中提取文本、标题和文件路径，并对提取的文本进行清洗处理。

    :param pdf_path: PDF 文件路径（字符串或 Path 对象）
    :return: 一个字典，包含 'title'、'content' 和 'path'，如果解析失败则返回 None
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # 提取第一页文本（通常包含标题）
            first_page = pdf.pages[0].extract_text() or ""
            # 提取最后一页文本（可能包含参考文献等信息）
            last_page = pdf.pages[-1].extract_text() or ""
            # 提取其他页的文本（例如第2-4页）
            middle_pages = [p.extract_text() or "" for p in pdf.pages[1:4] if p]

            # 将各部分文本合并，并转换为小写
            content = "\n".join([first_page] + middle_pages + [last_page]).lower()

            # 调用清洗函数，过滤掉 cid: 标记和对连写单词进行处理
            content = clean_extracted_text(content, use_wordninja=True)

            return {
                "title": Path(pdf_path).stem,
                "content": content,
                "path": str(pdf_path)
            }
    except Exception as e:
        print(f"解析失败：{pdf_path} - {str(e)}")
        return None
