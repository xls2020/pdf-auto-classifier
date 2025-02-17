# src/text_cleaner.py
import re

def clean_extracted_text(text, use_wordninja=False):
    """
    清洗 PDF 提取的文本：
      1. 移除形如 (cid:48) 和 cid:48 的标记。
      2. 在小写字母与大写字母之间插入空格（例如将 "sametransition" 转换为 "same transition"，对于部分情况可能有帮助）。
      3. 在字母与括号之间插入空格。
      4. 清除多余的空格。
      5. 可选：利用 wordninja 对连续较长的小写单词进行分词，解决单词连写问题。

    :param text: 待清洗的文本字符串
    :param use_wordninja: 如果为 True，则使用 wordninja 进一步分词（需要安装 wordninja）
    :return: 清洗后的文本
    """
    # 1. 移除形如 (cid:48) 的标记（包括括号内内容）
    text = re.sub(r'\(cid:\d+\)', '', text)
    # 2. 移除独立出现的 cid:48 这样的标记
    text = re.sub(r'cid:\d+', '', text)
    
    # 3. 在小写字母与大写字母之间插入空格
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    
    # 4. 在字母和左括号之间插入空格（如果缺失）
    text = re.sub(r'([a-zA-Z])\(', r'\1 (', text)
    # 5. 在右括号和字母之间插入空格（如果缺失）
    text = re.sub(r'\)([a-zA-Z])', r') \1', text)
    
    # 6. 去除多余空格
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 7. 可选：使用 wordninja 分词处理连在一起的长单词
    if use_wordninja:
        try:
            import wordninja
            tokens = text.split()
            new_tokens = []
            for token in tokens:
                # 对于全小写且长度较长的单词尝试分词
                if len(token) > 12 and token.islower():
                    splitted = wordninja.split(token)
                    new_tokens.extend(splitted)
                else:
                    new_tokens.append(token)
            text = " ".join(new_tokens)
        except ImportError:
            # 如果未安装 wordninja，则跳过这一步
            pass

    return text
