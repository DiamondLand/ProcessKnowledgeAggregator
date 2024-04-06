import random
import string


# --- Генерация текста для каптчи --- #
def generate_captcha_text(length=6):
    captcha_chars = string.ascii_letters + string.digits
    captcha = ''.join(random.choice(captcha_chars) for _ in range(length))
    return captcha
