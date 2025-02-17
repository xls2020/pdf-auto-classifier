import os
import shutil
import re
import unicodedata
from pathlib import Path

def fix_filename(filename: str) -> str:
    """
    对文件名进行归一化：
      - Unicode NFC 归一化
      - 去除前后空白
      - 替换多个空格为单个空格
      - 移除控制字符
    """
    fixed = unicodedata.normalize('NFC', filename)
    fixed = fixed.strip()
    fixed = re.sub(r'\s+', ' ', fixed)
    fixed = re.sub(r'[\x00-\x1f\x7f]', '', fixed)
    return fixed

def find_similar_file(directory: Path, target_filename: str) -> Path:
    """
    在 directory 目录下查找 PDF 文件，其归一化文件名与 target_filename 归一化后的名称相同，
    如果找到则返回该文件的 Path，否则返回 None。
    """
    target_fixed = fix_filename(target_filename)
    for file in directory.iterdir():
        if file.is_file() and file.suffix.lower() == '.pdf':
            if fix_filename(file.name) == target_fixed:
                return file
    return None

def get_long_path(path: Path) -> str:
    """
    如果在 Windows 系统下且路径较长，则返回带 "\\?\" 前缀的路径，否则返回普通绝对路径字符串。
    """
    abspath = str(path.resolve())
    if os.name == 'nt' and not abspath.startswith('\\\\?\\'):
        return '\\\\?\\' + abspath
    return abspath

def robust_transfer_pdfs(source_folder: Path, destination_folder: Path, error_log_file: Path, use_move=False):
    """
    递归查找 source_folder 下的 PDF 文件，并复制/移动到 destination_folder。
    若文件不存在，则尝试通过归一化后的文件名搜索匹配的文件。
    传输出错时，记录错误信息到 error_log_file，然后继续处理其它文件。
    
    参数:
      source_folder: 源文件夹
      destination_folder: 目标文件夹
      error_log_file: 错误日志文件路径
      use_move: True 使用移动操作，False 使用复制操作（默认 False）
    """
    error_log = []
    destination_folder.mkdir(parents=True, exist_ok=True)

    for current_dir, dirs, files in os.walk(source_folder):
        current_dir = Path(current_dir)
        # 排除目标文件夹
        if destination_folder.resolve() in current_dir.resolve().parents or current_dir.resolve() == destination_folder.resolve():
            continue
        if 'output' in dirs:
            dirs.remove('output')
        
        for file in files:
            if file.lower().endswith('.pdf'):
                src_file = current_dir / file

                # 如果原始路径不存在，则尝试通过归一化名称查找相似文件
                if not src_file.exists():
                    similar = find_similar_file(current_dir, file)
                    if similar is not None:
                        print(f"通过修正文件名找到：{similar}")
                        src_file = similar
                    else:
                        error_message = f"文件未找到：原名[{file}] 在目录：{current_dir}"
                        print("错误：", error_message)
                        error_log.append(error_message)
                        continue

                dst_file = destination_folder / file
                # 自动重命名，防止目标文件冲突
                if dst_file.exists():
                    base = dst_file.stem
                    ext = dst_file.suffix
                    count = 1
                    new_name = f"{base}_{count}{ext}"
                    dst_file = destination_folder / new_name
                    while dst_file.exists():
                        count += 1
                        new_name = f"{base}_{count}{ext}"
                        dst_file = destination_folder / new_name

                try:
                    if use_move:
                        src_long = get_long_path(src_file)
                        dst_long = get_long_path(dst_file)
                        shutil.move(src_long, dst_long)
                        print(f"已移动：{src_file} -> {dst_file}")
                    else:
                        try:
                            shutil.copy2(src_file, dst_file)
                            print(f"已复制：{src_file} -> {dst_file}")
                        except FileNotFoundError as e:
                            # 如果因路径过长未找到，尝试使用长路径前缀
                            src_long = get_long_path(src_file)
                            dst_long = get_long_path(dst_file)
                            shutil.copy2(src_long, dst_long)
                            print(f"已复制（长路径）：{src_file} -> {dst_file}")
                except Exception as e:
                    error_message = f"传输 {src_file} 时发生错误：{e}"
                    print("错误：", error_message)
                    error_log.append(error_message)

    if error_log:
        with error_log_file.open("w", encoding="utf-8") as f:
            for err in error_log:
                f.write(err + "\n")
        print(f"错误信息已保存至 {error_log_file}")
    else:
        print("所有文件传输均成功，无错误。")

if __name__ == "__main__":
    source_folder = Path(__file__).parent.resolve()
    destination_folder = source_folder / "output"
    error_log_file = source_folder / "problematic_documents.txt"
    
    # 设置 use_move 为 True 则使用移动操作，否则使用复制操作
    robust_transfer_pdfs(source_folder, destination_folder, error_log_file, use_move=False)

