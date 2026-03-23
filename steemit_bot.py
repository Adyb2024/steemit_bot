import os
import requests
import google.generativeai as genai
from beem import Steem
from datetime import datetime
import time

# --- [1] جلب الإعدادات ---
STEEM_USER = os.getenv("STEEM_USER", "whalemind")
POSTING_KEY = os.getenv("POSTING_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_KEY")

# التحقق من المفاتيح
if not POSTING_KEY:
    raise ValueError("❌ POSTING_KEY غير موجود في البيئة")
if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_KEY غير موجود في البيئة")

# إعداد Gemini 2.5
try:
    genai.configure(api_key=GEMINI_API_KEY)
    
    # استخدام نموذج Gemini 2.5 Flash (متاح ومستقر) [citation:4][citation:6]
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # بديل: إذا أردت النسخة التجريبية الأحدث:
    # model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
    
    # بديل: إذا أردت النسخة Pro للمهام الأكثر تعقيداً:
    # model = genai.GenerativeModel('gemini-2.5-pro')
    
    print("✅ تم تهيئة Gemini 2.5 Flash بنجاح")
    
    # عرض معلومات النموذج (اختياري للتحقق)
    print(f"📌 النموذج: gemini-2.5-flash | تاريخ المعرفة: يناير 2025 [citation:1][citation:6]")
    
except Exception as e:
    print(f"⚠️ خطأ في تهيئة Gemini: {e}")
    model = None

def get_market_intelligence():
    """جلب بيانات السوق من CoinGecko"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "bitcoin",
            "vs_currencies": "usd",
            "include_24hr_change": "true"
        }
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        print("📊 جاري جلب بيانات السوق...")
        response = requests.get(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        print(f"📥 البيانات المستلمة: {data}")
        
        if not data or 'bitcoin' not in data:
            raise ValueError("بيانات Bitcoin غير متوفرة")
            
        btc_data = data['bitcoin']
        btc_price = btc_data.get('usd', 0)
        change_24h = btc_data.get('usd_24h_change', 0)
        
        sentiment = "صعودي 🔥" if change_24h > 0 else "هبوطي ❄️"
        
        return {
            "price": f"{btc_price:,.0f}",
            "sentiment": sentiment,
            "change": f"{change_24h:+.2f}%"
        }
    except Exception as e:
        print(f"❌ CoinGecko Error: {e}")
        return {
            "price": "غير متاح",
            "sentiment": "متذبذب 📊",
            "change": "0%"
        }

def generate_human_post(market_data):
    """توليد المحتوى باستخدام Gemini 2.5 Flash"""
    if not model:
        return generate_fallback_post(market_data)
    
    prompt = f"""
    أنت محلل أسواق متمرس. اكتب منشوراً لـ Steemit باللغة العربية.
    
    بيانات السوق:
    - سعر البيتكوين: ${market_data['price']}
    - التغير خلال 24 ساعة: {market_data['change']}
    - الاتجاه: {market_data['sentiment']}
    
    المتطلبات:
    1. ابدأ بـ "Title:" ثم عنوان جذاب بالعربية
    2. استخدم أسلوباً عميقاً مع لمحات فلسفية عن الجشع والسلطة (48 Laws of Power)
    3. حلل حركة السعر كصراع بين الحيتان
    4. استخدم لغة بشرية وتعبيرات مثل: "لنكن صريحين"، "المفاجأة الحقيقية"
    5. استخدم Markdown للعناوين والاقتباسات
    6. اختم بسؤال مثير للجدل لجمع التعليقات
    7. أضف 5 علامات مناسبة
    
    اكتب منشوراً طويلاً وغني بالمعلومات (400-600 كلمة).
    """
    
    try:
        print("🤖 جاري توليد المحتوى باستخدام Gemini 2.5 Flash...")
        
        # Gemini 2.5 يدعم معلمات إضافية مثل درجة الحرارة [citation:1][citation:6]
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.8,  # تحكم في الإبداعية (0-2) [citation:1]
                "top_p": 0.95,       # تنويع الكلمات [citation:6]
                "max_output_tokens": 2048,  # الحد الأقصى للإخراج [citation:1]
            }
        )
        return response.text
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        return generate_fallback_post(market_data)

def generate_fallback_post(market_data):
    """محتوى احتياطي في حال فشل Gemini"""
    return f"""Title: تحليل السوق {datetime.now().strftime('%d/%m/%Y')}

**بيانات السوق الحالية:**
- سعر البيتكوين: ${market_data['price']}
- التغير خلال 24 ساعة: {market_data['change']}
- الاتجاه: {market_data['sentiment']}

**تحليل Gemini 2.5 Flash:**
السوق يشهد حركة نشطة مع تغيرات واضحة. مستوى ${market_data['price']} يعتبر نقطة محورية مهمة في الوقت الحالي.

**التحليل النفسي للسوق:**
المستثمرون يظهرون {market_data['sentiment']} اتجاهًا مع هذه التحركات. من المهم مراقبة سلوك الحيتان الكبار في السوق.

**نصائح التداول:**
1. استخدم إدارة رأس المال بحكمة
2. لا تتخذ قرارات عاطفية
3. راقب مستويات الدعم والمقاومة حول ${market_data['price']}
4. تابع الأخبار المؤثرة على السوق

**ختاماً:**
ما رأيك في تحركات السوق الحالية؟ هل تتوقع استمرار هذا الاتجاه أم هناك تصحيح قادم؟ شاركنا تعليقك أدناه.

#crypto #bitcoin #steemexclusive #trading #analysis #gemini25
"""

def publish_to_steemit(content):
    """نشر المحتوى على Steemit - النسخة المصححة"""
    try:
        # [1] استخراج العنوان والمحتوى كما فعلت بنجاح
        lines = content.split('\n')
        title = None
        body_lines = []
        for line in lines:
            if 'Title:' in line and not title:
                title = line.split(':', 1)[1].strip().replace('**', '').replace('#', '')
            else:
                body_lines.append(line)
        
        if not title:
            title = f"رؤية الحوت الرقمي {datetime.now().strftime('%Y-%m-%d')}"
        
        body = '\n'.join(body_lines)
        footer = f"\n---\n*Written by WhaleMind AI (Gemini 2.5) | {datetime.now().strftime('%Y-%m-%d')}*"

        # [2] النشر (تعديل طريقة الاتصال)
        print(f"📤 جاري النشر باسم {STEEM_USER}...")
        
        # استخدام نود (Nodes) موثوقة مباشرة
        stm = Steem(node=["https://api.steemit.com", "https://anyx.io"], keys=[POSTING_KEY])
        
        # النشر المباشر (المكتبة ستتحقق من الحساب تلقائياً عند النشر)
        stm.post(
            title=title[:255],
            body=body + footer,
            author=STEEM_USER,
            tags=["crypto", "steemexclusive", "trading", "arabic", "gemini25"],
            self_vote=False
        )
        
        print(f"✅ تم النشر بنجاح: {title}")
        return True
        
    except Exception as e:
        print(f"❌ فشل النشر النهائي: {str(e)}")
        return False
