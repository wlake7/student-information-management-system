# wl31/utils/hash_utils.py
# 描述: 提供密码哈希和验证功能

import bcrypt

def hash_password(password: str) -> str:
    """
    使用 bcrypt 对密码进行哈希处理。
    :param password: 明文密码。
    :return: 哈希后的密码字符串。
    """
    # 生成盐并哈希密码
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码是否与哈希值匹配。
    :param plain_password: 用户输入的明文密码。
    :param hashed_password: 数据库中存储的哈希密码。
    :return: 如果密码匹配则返回 True，否则返回 False。
    """
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except (ValueError, TypeError):
        # 如果哈希格式不正确或为空，则返回False
        return False

if __name__ == '__main__':
    # 测试代码
    plain_text = "mysecretpassword123"
    hashed = hash_password(plain_text)
    
    print(f"Plain text: {plain_text}")
    print(f"Hashed: {hashed}")
    
    # 测试验证
    is_correct = verify_password(plain_text, hashed)
    print(f"Verification with correct password: {is_correct}") # 应该为 True
    
    is_correct = verify_password("wrongpassword", hashed)
    print(f"Verification with incorrect password: {is_correct}") # 应该为 False