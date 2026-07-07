import os
import json
import re
from datetime import datetime
import google.generativeai as genai

# ۱. پیکربندی موتور هوش مصنوعی گوگل
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

# ۲. فراخوانی حافظه تاریخی سیستم
json_db_str = read_file('decisions-log.json', '[]')
md_trends = read_file('weekly-trends.md', '# روندهای هفتگی دیده‌بان کسب‌وکار (Weekly Trends)\n')

try:
    historical_db = json.loads(json_db_str)
except:
    historical_db = []

today_str = datetime.now().strftime('%Y-%m-%d')

# ۳. تدوین پرامپت مهندسی‌شده
prompt_text = f"""
امروز {today_str} است. تو یک تحلیلگر ارشد استراتژی محصول و معمار زیرساخت‌های SaaS هستی.
وظیفه تو رصد زنده، کالبدشکافی عمیق و مستندسازی تصمیمات فنی/مدیریتی شرکت‌های پیشرو تکنولوژی در دنیا است.

Analyse recent web signals for pivots, pricing model changes, cloud infrastructure shifts, cost-cutting strategies, and practical AI deployments in companies like Stripe, Shopify, OpenAI, Netflix, Meta, Uber, Airbnb, and notable Y-Combinator startups.

با تحلیل داده‌های جدید و ترکیب آن‌ها با حافظه تاریخی سیستم ما، ۳ خروجی مجزا و دقیق تولید کن.

[حافظه تاریخی دیتابیس (۵ ردیف آخر جهت جلوگیری از تکرار)]:
{json.dumps(historical_db[-5:], indent=2, ensure_ascii=False)}

[روندهای کلان ثبت شده تا کنون]:
{md_trends}

خروجی‌های خود را دقیقاً درون تگ‌های مشخص شده قرار بده. هیچ متن، توضیح یا تعارفی خارج از تگ‌ها ننویس:

<html_output>
یک داشبورد مدیریتی فوق‌العاده شیک، مینیمال، مدرن و کاملاً فارسی (index.html).
از فونت Vazirmatn (از طریق گوگل‌فونتس)، ساختار گرید (Grid Layout)، تم رنگی لوکس، نشانگرهای کیفیت منبع (۱ تا ۵ ستاره)، بخش "چرا اهمیت دارد"، بخش "اقدام امروز برای استارتاپ شما" و دسته‌بندی‌های رنگی (pricing, infrastructure, product-pivot, ai-integration) استفاده کن. طراحی باید کاملاً Responsive باشد.
</html_output>

<json_output>
یک آرایه JSON (فقط رکوردهای استخراج شده امروز) که هر آبجکت آن دقیقاً دارای این فیلدهای مهندسی‌شده باشد:
{{
  "date": "{today_str}",
  "company": "نام شرکت",
  "category": "دسته‌بندی دقیق",
  "problem": "مسئله یا چالشی که شرکت با آن مواجه بود",
  "hypothesis": "فرضیه تیم مدیریت/فنی برای حل مسئله",
  "experiment_or_action": "اقدام عملی یا آزمایشی که انجام دادند",
  "metric_tracked": "متریک اصلی برای سنجش موفقیت",
  "decision_outcome": "تصمیم نهایی اتخاذ شده",
  "core_lesson": "درس‌آموخته جهانی و بیزینسی برای استارتاپ‌های دیگر",
  "source_name": "نام منبع معتبر",
  "source_url": "لینک دقیق منبع",
  "source_quality_stars": 5
}}
</json_output>

<md_output>
کل متن فایل weekly-trends.md را بازنویسی کن. به این صورت که روندهای تحلیل‌شده امروز را به عنوان یک آیتم جدید با فرمت زیر به لیست روندهای فعلی اضافه کن:
- **{today_str}:** خلاصه روند تحلیلی کلان | *Tags: tag1, tag2*
متن‌های قبلی موجود در فایل را حتماً در ادامه حفظ کن.
</md_output>
"""

try:
    # ۴. استفاده از آبجکت صریح پروتوباف برای فعال‌سازی قطعی ابزار سرچ گوگل بدون تداخل با باگ SDK پایتون
    google_search_tool = genai.protos.Tool(google_search={})
    
    model = genai.GenerativeModel(
        'gemini-2.5-flash',
        tools=[google_search_tool]
    )
    
    response = model.generate_content(prompt_text)
    raw_response = response.text
    
    # ۵. استخراج داده‌ها به روش XML Parsing
    html_content = re.search(r'<html_output>(.*?)</html_output>', raw_response, re.DOTALL).group(1).strip()
    json_content = re.search(r'<json_output>(.*?)</json_output>', raw_response, re.DOTALL).group(1).strip()
    md_content = re.search(r'<md_output>(.*?)</md_output>', raw_response, re.DOTALL).group(1).strip()
    
    # ۶. پارس آرایه JSON و الصاق آن به دیتابیس اصلی
    try:
        new_records = json.loads(json_content)
        if isinstance(new_records, list):
            historical_db.extend(new_records)
        elif isinstance(new_records, dict):
            historical_db.append(new_records)
    except Exception as e:
        print(f"JSON Parsing failed, appending raw data instead: {e}")
        historical_db.append({
            "date": today_str,
            "error": "Failed to parse structured JSON",
            "raw_text": json_content[:500]
        })

    # ۷. ذخیره‌سازی همزمان هر ۳ سند در مخزن گیت‌هاب
    write_file('index.html', html_content)
    write_file('decisions-log.json', json.dumps(historical_db, indent=2, ensure_ascii=False))
    write_file('weekly-trends.md', md_content)
    
    print("🚀 [SUCCESS] Business Bulletin Core updated with premium analytics and grounding database!")

except Exception as main_error:
    print(f"💥 [CRITICAL ERROR] Core Execution Failed: {main_error}")
    fallback_html = f"""
    <div style='font-family:sans-serif; padding:50px; text-align:center; color:#333; direction:rtl;'>
        <h2>⚠️ سیستم دیده‌بان در حال به‌روزرسانی زیرساخت است</h2>
        <p>موتور استراتژی خطایی را گزارش کرده است. فرآیند خودمراقبتی سیستم فعال شده است.</p>
        <code style='background:#fff5f5; color:#c53030; padding:10px; border-radius:5px; display:inline-block; direction:ltr;'>{main_error}</code>
    </div>
    """
    write_file('index.html', fallback_html)
