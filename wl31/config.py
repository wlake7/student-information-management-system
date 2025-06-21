# wl31/config.py

import os

# 项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 数据库文件路径
DATABASE_PATH = os.path.join(BASE_DIR, "wl31.db")

# 验证码字体目录
CAPTCHA_FONT_DIR = os.path.join(BASE_DIR, "assets", "captcha_fonts")

# 默认字体（如果需要）
# DEFAULT_FONT_PATH = os.path.join(CAPTCHA_FONT_DIR, "your_font.ttf")