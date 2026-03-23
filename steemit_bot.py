import os
import requests
import google.generativeai as genai
from beem import Steem
from datetime import datetime

# --- [1] جلب الإعدادات من GitHub Secrets ---
STEEM_USER = os.getenv("STEEM_USER", "whalemind")
POSTING_KEY = os.getenv("POSTING_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_KEY")

# إعداد ذكاء Gemini (الموديل 2.5 كما طلبت)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

def get_market_intelligence():
    try:
        # جلب البيانات من CoinGecko بدل بينانس
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&include_24hr_change=true"
        response = requests.get(url, timeout=15).json()
        
        btc_price = response['bitcoin']['usd']
        change_24h = response['bitcoin']['usd_24h_change']
        
        sentiment = "صعودي" if change_24h > 0 else "هبوطي"
        
        return {
            "price": f"{btc_price:,}",
            "sentiment": sentiment,
            "change": f"{change_24h:.2f}%"
        }
    except Exception as e:
        print(f"CoinGecko Error: {e}")
        return {"price": "غير متاح", "sentiment": "متذبذب", "change": "0%"}

def generate_human_post(market_data):
    # البرومبت بأسلوب 48 قانوناً للقوة وهندسة الفضول
    prompt = f"""
    Context: Bitcoin price is ${market_data['price']} ({market_data['change']}) and trend is {market_data['sentiment']}.
    Task: Write a deep, cinematic Steemit post in ARABIC. 
    Style: Shadow Analyst, 48 Laws of Power, dark psychology.
    
    IMPORTANT: The first line MUST be: 'Title: [Your Creative Arabic Title]'
    
    Guidelines:
    1. ابدأ بفكرة فلسفية صادمة عن الجشع البشري أو السيطرة.
    2. حلل حركة السعر كأنها "صراع حيتان" وليست مجرد أرقام.
    3. استخدم عبارات بشرية مثل: "لنكن صريحين"، "المفاجأة الحقيقية هي"، "لقد رأيت هذا السيناريو من قبل".
    4. التنسيق: Markdown (Bold headers, blockquotes).
    5. النهاية: سؤال مثير للجدل لجمع التعليقات.
    
    Tags: #crypto #steemexclusive #psychology #trading #arabic #finance
    """
    response = model.generate_content(prompt)
    return response.text

def publish_to_steemit(content):
    try:
        lines = [l for l in content.split('\n') if l.strip()]
        
        # استخراج العنوان
        if "Title:" in lines[0] or "عنوان:" in lines[0]:
            title = lines[0].split(':')[-1].replace('**', '').strip()
            body = '\n'.join(lines[1:])
        else:
            title = f"خلف كواليس السوق: سيكولوجية الحيتان {datetime.now().strftime('%H:%M')}"
            body = content
        
        footer = f"\n\n---\n*تم التوليد بواسطة WhaleMind (Gemini 2.5) | {datetime.now().strftime('%Y-%m-%d')}*"
        
        # النشر
        stm = Steem(keys=[POSTING_KEY])
        tags = ["crypto", "steemexclusive", "psychology", "trading", "arabic"]
        
        print(f"جاري إرسال المقال إلى بلوكشين Steem باسم {STEEM_USER}...")
        stm.post(title=title, body=body + footer, author=STEEM_USER, tags=tags, self_vote=True)
        print(f"✅ تم النشر بنجاح: {title}")
        
    except Exception as e:
        print(f"❌ فشل النشر: {str(e)}")

if __name__ == "__main__":
    print(f"بدء تشغيل بوت WhaleMind (النسخة 2.5) - الوقت: {datetime.now()}")
    data = get_market_intelligence()
    post_content = generate_human_post(data)
    publish_to_steemit(post_content)
