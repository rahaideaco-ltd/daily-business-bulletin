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

# پرامپت سیستمی و درخواست اصلی
prompt = f"""
تو یک تحلیلگر ارشد استراتژی کسب‌وکار هستی. اخبار مهم تک و SaaS امروز را مرور کن و بولتن روزانه را بساز.
فایل‌های دیتابیس قبلی اینها هستند:
JSON Database:
{json_db}

Markdown Trends:
{md_trends}

خروجی خود را دقیقاً در ۳ بلوک کد مجزا (بدون هیچ متن اضافه‌ای) ارائه بده:
1. بلوک کد HTML قالب گزارش
2. بلوک کد JSON آپدیت شده
3. بلوک کد Markdown آپدیت شده
"""

# فراخوانی مدل
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content(prompt)
text = response.text

# استخراج بلوک‌های کد از خروجی هوش مصنوعی
html_match = re.search(r'```html(.*?)```', text, re.DOTALL)
json_match = re.search(r'```json(.*?)```', text, re.DOTALL)
md_match = re.search(r'```markdown(.*?)```', text, re.DOTALL)

if html_match and json_match and md_match:
    # ذخیره فایل HTML به عنوان index.html برای نمایش در GitHub Pages
    write_file('index.html', html_match.group(1))
    # آپدیت دیتابیس‌ها
    write_file('decisions-log.json', json_match.group(1))
    write_file('weekly-trends.md', md_match.group(1))
    print("Files successfully generated and updated.")
else:
    print("Error: Could not parse all code blocks from the AI response.")
