import os
import json
from datetime import datetime
import google.generativeai as genai

# ۱. تنظیم کلید API
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def read_file(filepath, default_content=""):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return default_content

def write_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip())

# ۲. خواندن حافظه تاریخی سیستم
json_db_str = read_file('decisions-log.json', '[]')
md_trends = read_file('weekly-trends.md', '# Weekly Meta Trends\n')

try:
    historical_data = json.loads(json_db_str)
except:
    historical_data = []

today_str = datetime.now().strftime('%Y-%m-%d')

# ۳. طراحی پرامپت استراتژیک و چندمنظوره
prompt_text = f"""
تو یک تحلیلگر ارشد استراتژی کسب‌وکار و سیستم‌های SaaS هستی. 
امروز {today_str} است. ابتدا در وب جستجو کن و مهم‌ترین اخبار، تصمیمات استراتژیک شرکت‌های بزرگ (مثل OpenAI, Microsoft, Google, Stripe) و ابزارهای جدید معرفی شده در حوزه هوش مصنوعی و نرم‌افزار را پیدا کن.

سپس با ترکیب اخبار جدید امروز و تاریخچه بولتن‌های قبلی ما که در زیر آمده است، ۳ خروجی مجزا تولید کن:
---
[دیتابیس ساختاریافته روزهای قبل]:
{json.dumps(historical_data[-5:], indent=2, ensure_ascii=False)} 

[روندهای کلان ثبت شده تا کنون]:
{md_trends}
---

خروجی خود را دقیقاً در ۳ بلوک کد مجزا (بدون هیچ متن اضافی قبل یا بعد از بلوک‌ها) به فرمت زیر ارائه بده:

۱. بلوک اول (HTML): یک بولتن روزانه بسیار شیک، گرافیکی و مجله‌ای به زبان فارسی (index.html). شامل بخش خلاصه، اخبار داغ امروز همراه با منبع یا نام شرکت‌ها، ابزارهای جدید، و بخش "اقدام امروز".
۲. بلوک دوم (JSON): یک آبجکت ساختاریافته از دیتای امروز (فقط آبجکت امروز، نه کل آرایه) شامل:
"date": "{today_str}", "top_news": ["خلاصه خبر ۱", "خلاصه خبر ۲"], "tools": ["ابزار ۱", "ابزار ۲"]
۳. بلوک سوم (MARKDOWN): تحلیل تو از تغییر روندهای کلان بر اساس اخبار امروز و دیتای روزهای گذشته برای اضافه شدن به فایل روندهای هفتگی.

پاسخ را دقیقاً با تگ‌های ```html و ```json و ```markdown تفکیک کن.
"""

try:
    # ۴. فعال‌سازی مدل با قابلیت سرچ زنده در گوگل (Google Search Tooling)
    model = genai.GenerativeModel(
        'gemini-2.5-flash',
        tools=[{"google_search": {}}]
    )
    
    response = model.generate_content(prompt_text)
    text_response = response.text
    
    # ۵. تفکیک هوشمند خروجی‌ها با استفاده از Split
    html_part = text_response.split("```html")[1].split("```")[0].strip()
    json_part = text_response.split("```json")[1].split("```")[0].strip()
    md_part = text_response.split("```markdown")[1].split("```")[0].strip()
    
    # ۶. به‌روزرسانی و غنی‌سازی دیتابیس متمرکز (JSON)
    try:
        today_json_data = json.loads(json_part)
        historical_data.append(today_json_data)
    except Exception as json_err:
        print(f"JSON Parse error, creating fallback: {json_err}")
        historical_data.append({
            "date": today_str,
            "status": "Generated with formatting notice",
            "raw_note": "دیتای امروز به دلیل فرمت متنی استخراج دستی شد."
        })

    # ۷. ذخیره‌سازی همزمان هر ۳ فایل برای گیت‌هاب پیجز و آرشیو
    write_file('index.html', html_part)
    write_file('decisions-log.json', json.dumps(historical_data, indent=2, ensure_ascii=False))
    write_file('weekly-trends.md', md_part)
    
    print("Success: Real-time data fetched, JSON database enriched, and HTML generated!")

except Exception as e:
    print(f"Main System Error: {e}")
    # ثبت خطا در لوپ برای جلوگیری از خرابی فرآیند اتوماسیون
    write_file('index.html', f"<h1>Error in Strategy Engine: {e}</h1>")
