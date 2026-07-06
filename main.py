import os
import json
import google.generativeai as genai

# تنظیم کلید API
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

# خواندن دیتابیس‌ها
json_db = read_file('decisions-log.json', '[]')
md_trends = read_file('weekly-trends.md', '# Weekly Meta Trends\n')

# تعریف پرامپت با ساختار کاملاً ایمن
prompt_text = "تو یک تحلیلگر ارشد استراتژی کسب‌وکار هستی. اخبار مهم تک، SaaS و هوش مصنوعی امروز (تاریخ: 2026-07-06) را مرور کن و یک بولتن روزانه شیک و کامل به زبان فارسی با فرمت استاندارد HTML بساز.\n"
prompt_text += "قالب طراحی باید عینا شامل یک هدر مجله‌ای زیبا با عنوان 'دیده‌بان روزانه کسب‌وکار'، بخش خلاصه در یک نگاه (Glance)، بخش‌های اخبار، تصمیمات شرکت‌های پیشرو، ابزارهای جدید و بخش اقدام امروز باشد.\n"
prompt_text += f"این هم داده‌های تاریخی دیتابیس برای تحلیل روندها:\n{md_trends}"

try:
    # فراخوانی مدل سریع و پایدار
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt_text)
    html_content = response.text
    
    # پاک‌سازی تگ‌های احتمالی مارک‌داون اطراف HTML
    if "```html" in html_content:
        html_content = html_content.split("```html")[1].split("```")[0]
    elif "```" in html_content:
        html_content = html_content.split("```")[1].split("```")[0]

    # ذخیره فایل اصلی سایت
    write_file('index.html', html_content)
    
    # یک رکورد ساده هم برای خالی نماندن دیتابیس اضافه میکنیم
    try:
        data = json.loads(json_db)
    except:
        data = []
    data.append({"date": "2026-07-06", "status": "Generated Successfully"})
    write_file('decisions-log.json', json.dumps(data, indent=2))
    
    print("Success: index.html has been created successfully!")

except Exception as e:
    print(f"An error occurred: {e}")
    write_file('index.html', f"<h1>Error in generation: {e}</h1>")
