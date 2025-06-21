# wl31/utils/pinyin_utils.py
from pypinyin import pinyin, Style

def convert_to_pinyin_initials(text):
    """
    将中文字符串转换为拼音首字母缩写。
    例如: "张三" -> "zs"
    """
    if not text:
        return ""
    # 使用 pypinyin 库获取首字母
    initials = pinyin(text, style=Style.INITIALS, strict=False)
    # 将 [['z'], ['s']] 格式的结果连接成 "zs"
    return "".join([item[0] for item in initials])