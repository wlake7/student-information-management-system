# wl31/utils/captcha.py
# 描述: 生成图形验证码

import random
from PIL import Image, ImageDraw, ImageFont
import os
from wl31 import config

class Captcha:
    """
    图形验证码生成器
    """
    def __init__(self, width=150, height=60, length=4):
        self.width = width
        self.height = height
        self.length = length
        self.char_set = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'
        self.font_paths = self._get_font_paths()

    def _get_font_paths(self):
        """获取字体文件路径列表"""
        font_dir = config.CAPTCHA_FONT_DIR
        if not os.path.exists(font_dir) or not os.path.isdir(font_dir):
            # 如果字体目录不存在，返回空列表，后续会使用默认字体
            os.makedirs(font_dir, exist_ok=True)
            print(f"Warning: Captcha font directory '{font_dir}' not found or is empty. A default font will be used.")
            return []
        
        paths = [os.path.join(font_dir, f) for f in os.listdir(font_dir) if f.lower().endswith(('.ttf', '.otf'))]
        if not paths:
            print(f"Warning: No font files found in '{font_dir}'. A default font will be used.")
        return paths

    def _get_random_font(self):
        """随机获取一个字体"""
        if self.font_paths:
            font_path = random.choice(self.font_paths)
            font_size = random.randint(35, 45)
            return ImageFont.truetype(font_path, font_size)
        else:
            # 如果没有找到字体文件，使用Pillow的默认字体
            try:
                return ImageFont.load_default(size=40)
            except AttributeError: # For newer Pillow versions
                 return ImageFont.load_default()


    def _get_random_color(self):
        """随机获取一个颜色"""
        return (random.randint(30, 150), random.randint(30, 150), random.randint(30, 150))

    def generate(self):
        """
        生成验证码图片和对应的字符串
        :return: (验证码字符串, PIL.Image对象)
        """
        image = Image.new('RGB', (self.width, self.height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        captcha_text = ''.join(random.choices(self.char_set, k=self.length))
        
        # 绘制验证码字符
        font = self._get_random_font()
        char_width = self.width / self.length
        for i, char in enumerate(captcha_text):
            x = int(char_width * i + random.randint(0, 5))
            y = random.randint(0, 10)
            draw.text((x, y), char, font=font, fill=self._get_random_color())

        # 绘制干扰线
        for _ in range(5):
            x1 = random.randint(0, self.width)
            y1 = random.randint(0, self.height)
            x2 = random.randint(0, self.width)
            y2 = random.randint(0, self.height)
            draw.line((x1, y1, x2, y2), fill=self._get_random_color())

        # 绘制干扰点
        for _ in range(50):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            draw.point((x, y), fill=self._get_random_color())

        return captcha_text, image

if __name__ == '__main__':
    # 测试代码
    captcha_generator = Captcha()
    text, img = captcha_generator.generate()
    print(f"Generated Captcha Text: {text}")
    # 为了在没有GUI环境的情况下测试，将图片保存到文件
    test_image_path = os.path.join(config.BASE_DIR, "captcha_test.png")
    img.save(test_image_path)
    print(f"Captcha image saved to: {test_image_path}")