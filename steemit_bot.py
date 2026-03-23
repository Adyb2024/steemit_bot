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

# إعداد Gemini
try:
    genai.configure(api_key=GEMINI_API_KEY)
    # استخدام نموذج متاح
    model = genai.GenerativeModel('gemini-1.5-flash')  # أو 'gemini-pro'
    print("✅ تم تهيئة Gemini بنجاح")
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
        # بيانات احتياطية
        return {
            "price": "83,500",
            "sentiment": "متذبذب 📊",
            "change": "+2.5%"
        }

def generate_human_post(market_data):
    """توليد المحتوى باستخدام Gemini"""
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
    6. اختم بسؤال مثير للجدل
    7. أضف 5 علامات مناسبة
    
    اكتب منشوراً طويلاً وغني بالمعلومات.
    """
    
    try:
        print("🤖 جاري توليد المحتوى...")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        return generate_fallback_post(market_data)

def generate_fallback_post(market_data):
    """محتوى احتياطي في حال فشل Gemini"""
    return f"""Title: تحليل السوق {datetime.now().strftime('%d/%m/%Y')}

**بيانات السوق الحالية:**
- سعر البيتكوين: ${market_data['price']}
- التغير: {market_data['change']}
- الاتجاه: {market_data['sentiment']}

**التحليل:**
السوق يشهد حركة نشطة مع تغيرات واضحة. من المهم متابعة مستويات الدعم والمقاومة.

**نصيحة اليوم:**
استخدم إدارة رأس المال بحكمة ولا تتخذ قرارات عاطفية.

*ما رأيك في تحركات السوق الحالية؟ شاركنا تعليقك أدناه.*

#crypto #bitcoin #steemexclusive #trading #analysis
"""

def publish_to_steemit(content):
    """نشر المحتوى على Steemit"""
    try:
        # استخراج العنوان
        lines = content.split('\n')
        title = None
        body_lines = []
        
        for line in lines:
            if 'Title:' in line and not title:
                title = line.split(':', 1)[1].strip()
                title = title.replace('**', '').strip()
            else:
                body_lines.append(line)
        
        if not title:
            title = f"تحليل السوق {datetime.now().strftime('%Y-%m-%d')}"
        
        body = '\n'.join(body_lines)
        
        # إضافة تذييل
        footer = f"""
---
*تم النشر بواسطة WhaleMind AI | {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
        
        # النشر
        print(f"📤 جاري النشر باسم {STEEM_USER}...")
        stm = Steem(keys=[POSTING_KEY])
        
        tags = ["crypto", "steemexclusive", "psychology", "trading", "arabic"]
        
        result = stm.post(
            title=title[:255],  # الحد الأقصى لطول العنوان
            body=body + footer,
            author=STEEM_USER,
            tags=tags,
            self_vote=False
        )
        
        print(f"✅ تم النشر بنجاح: {title}")
        print(f"🔗 الرابط: https://steemit.com/@{STEEM_USER}/")
        return True
        
    except Exception as e:
        print(f"❌ فشل النشر: {str(e)}")
        return False

if __name__ == "__main__":
    print(f"🚀 بدء تشغيل WhaleMind - {datetime.now()}")
    print(f"📌 Python version: {os.sys.version}")
    
    # جلب البيانات
    market_data = get_market_intelligence()
    print(f"📊 Bitcoin: ${market_data['price']} ({market_data['change']}) - {market_data['sentiment']}")
    
    # توليد المحتوى
    content = generate_human_post(market_data)
    
    # النشر
    if publish_to_steemit(content):
        print("🎉 انتهى التنفيذ بنجاح")
    else:
        print("⚠️ انتهى التنفيذ مع أخطاء")
