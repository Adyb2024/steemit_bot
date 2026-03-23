import os
import requests
import google.generativeai as genai
from beem import Steem
from beem.account import Account
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

print(f"📌 محاولة الاتصال بحساب: {STEEM_USER}")

# اختبار الاتصال بـ Steem أولاً
try:
    # محاولة اتصال أولية
    stm_test = Steem(keys=[POSTING_KEY])
    print("✅ تم تهيئة اتصال Steem")
    
    # محاولة جلب معلومات الحساب للتحقق
    try:
        account_info = stm_test.get_account(STEEM_USER)
        print(f"✅ تم التحقق من الحساب: {STEEM_USER}")
        print(f"📊 رصيد STEEM: {account_info.get('balance', 'غير متاح')}")
    except Exception as e:
        print(f"⚠️ تحذير: لا يمكن جلب معلومات الحساب - {e}")
        print("⏳ سنحاول النشر مباشرة...")
        
except Exception as e:
    print(f"❌ فشل الاتصال بـ Steem: {e}")
    print("⚠️ تأكد من صحة POSTING_KEY")
    exit(1)

# إعداد Gemini 2.5
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    print("✅ تم تهيئة Gemini 2.5 Flash بنجاح")
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
    2. استخدم أسلوباً عميقاً مع لمحات فلسفية عن الجشع والسلطة
    3. حلل حركة السعر كصراع بين الحيتان
    4. استخدم لغة بشرية وتعبيرات مثل: "لنكن صريحين"، "المفاجأة الحقيقية"
    5. استخدم Markdown للعناوين والاقتباسات
    6. اختم بسؤال مثير للجدل لجمع التعليقات
    
    اكتب منشوراً طويلاً وغني بالمعلومات.
    """
    
    try:
        print("🤖 جاري توليد المحتوى باستخدام Gemini 2.5 Flash...")
        
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.8,
                "top_p": 0.95,
                "max_output_tokens": 2048,
            }
        )
        return response.text
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        return generate_fallback_post(market_data)

def generate_fallback_post(market_data):
    """محتوى احتياطي في حال فشل Gemini"""
    return f"""Title: تحليل البيتكوين {datetime.now().strftime('%d/%m/%Y')}

**بيانات السوق الحالية:**
- سعر البيتكوين: ${market_data['price']}
- التغير خلال 24 ساعة: {market_data['change']}
- الاتجاه: {market_data['sentiment']}

**تحليل فني:**
السوق في حالة {market_data['sentiment']} مع اختراق لمستوى ${market_data['price']}.

**نقاط مهمة:**
1. الحجم يتزايد مع هذه الحركة
2. المقاومة التالية عند $72,000
3. الدعم عند $70,500

**ختاماً:**
هل تعتقد أن هذا الصعود سيستمر؟ شاركنا رأيك في التعليقات!

#crypto #bitcoin #steemexclusive #trading #analysis
"""

def publish_to_steemit(content):
    try:
        # استخراج العنوان والمحتوى
        lines = content.split('\n')
        title = lines[0].replace('Title:', '').replace('**', '').strip()
        body = '\n'.join(lines[1:])
        
        # الاتصال المباشر بمفتاح النشر
        # وضعنا النودز الأكثر استقراراً لضمان وصول المقال لـ whalemind
        stm = Steem(node=["https://api.steemit.com", "https://anyx.io"], keys=[POSTING_KEY])
        
        # النشر الفعلي
        print(f"📤 جاري إرسال المقال إلى بلوكشين Steem باسم whalemind...")
        stm.post(
            title=title[:255], 
            body=body, 
            author="whalemind", 
            tags=["crypto", "arabic", "gemini25", "trading"],
            self_vote=True
        )
        print("✅ مبروك يا أديب! تم النشر بنجاح.")
        return True
    except Exception as e:
        print(f"❌ فشل النشر النهائي: {str(e)}")
        return False
