import os
import requests
import google.genai as genai
from beem import Steem
from datetime import datetime
import time

# --- [1] جلب الإعدادات ---
STEEM_USER = os.getenv("STEEM_USER", "whalemind")
POSTING_KEY = os.getenv("POSTING_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_KEY")

# التحقق من المفاتيح
if not POSTING_KEY:
    raise ValueError("❌ POSTING_KEY غير موجود")
if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_KEY غير موجود")

# إعداد Gemini
client = genai.Client(api_key=GEMINI_API_KEY)

def get_market_intelligence():
    """جلب بيانات السوق مع بيانات احتياطية"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "bitcoin",
            "vs_currencies": "usd",
            "include_24hr_change": "true"
        }
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        
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
            "price": "غير متاح",
            "sentiment": "متذبذب 📊",
            "change": "0%"
        }

def generate_human_post(market_data):
    """توليد المحتوى باستخدام Gemini"""
    prompt = f"""
    Bitcoin is at ${market_data['price']} with {market_data['change']} change, trend is {market_data['sentiment']}.
    
    Write a Steemit post in ARABIC with this structure:
    
    Title: [Creative Arabic Title]
    
    Content:
    - Start with shocking philosophy about greed and power
    - Analyze price action as "whale war"
    - Use human expressions
    - End with controversial question
    
    Style: Dark psychology, 48 Laws of Power
    Format: Markdown with headers and quotes
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        return f"""Title: تحليل السوق {datetime.now().strftime('%d/%m/%Y')}

المحتوى غير متاح حالياً بسبب خطأ تقني. نعتذر عن الإزعاج."""

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
*تم التوليد بواسطة WhaleMind AI | {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
        
        # النشر
        stm = Steem(keys=[POSTING_KEY])
        tags = ["crypto", "steemexclusive", "psychology", "trading", "arabic"]
        
        print(f"📤 جاري النشر باسم {STEEM_USER}...")
        result = stm.post(
            title=title,
            body=body + footer,
            author=STEEM_USER,
            tags=tags,
            self_vote=False  # تجنب التصويت الذاتي
        )
        
        print(f"✅ تم النشر بنجاح: {title}")
        return True
        
    except Exception as e:
        print(f"❌ فشل النشر: {str(e)}")
        return False

if __name__ == "__main__":
    print(f"🚀 بدء تشغيل WhaleMind - {datetime.now()}")
    
    # جلب البيانات
    market_data = get_market_intelligence()
    print(f"📊 Bitcoin: ${market_data['price']} ({market_data['change']})")
    
    # توليد المحتوى
    print("🤖 جاري توليد المحتوى...")
    content = generate_human_post(market_data)
    
    # النشر
    if publish_to_steemit(content):
        print("🎉 انتهى التنفيذ بنجاح")
    else:
        print("⚠️ انتهى التنفيذ مع أخطاء")
