import os
import re
import google.generativeai as genai

# دریافت کلید API از تنظیمات گیت‌هاب
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def read_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""

def write_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip())

# خواندن دیتابیس‌های فعلی
json_db = read_file('decisions-log.json')
md_trends = read_file('weekly-trends.md')

# پرامپت کاملاً ساختاریافته برای اجبار مدل به تولید پاسخ دقیق
prompt = f"""
تو یک تحلیلگر ارشد استراتژی کسب‌وکار هستی. اخبار مهم تک، SaaS و هوش مصنوعی امروز (تاریخ امروز: 2026-07-06) را مرور کن و بولتن روزانه را بر اساس این داده‌های قبلی بساز.

فایل‌های دیتابیس قبلی:
JSON Database:
{json_db}

Markdown Trends:
{md_trends}

خروجی خود را دقیقاً و حتماً در ۳ بلوک کد مجزا با نام‌های دقیق زیر ارائه بده و هیچ متن اضافی قبل یا بعد از بلوک‌ها ننویس:

```html
(کد کامل HTML را اینجا قرار بده)
