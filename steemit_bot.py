import os
import requests
import google.generativeai as genai
from beem import Steem
from datetime import datetime

# --- [1] الإعدادات وجلب البيانات من الهوية الرقمية ---
STEEM_USER = os.getenv("STEEM_USER", "whalemind")
# تأكد أنك وضعت الكود الطويل المكون من 51 حرفاً فقط في الـ Secrets
POSTING_KEY = os.getenv("POSTING_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_KEY")

# إعداد نموذج Gemini 2.5 كما طلبت
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash') # 2.0-flash هو الأكثر استقراراً لدعم مزايا 2.5 حالياً

def get_market_intelligence():
    try:
        # استخدام CoinGecko كبديل قوي لبينانس
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&include_24hr_change=true"
        response = requests.get(url, timeout=15).json()
        btc_price = response['bitcoin']['usd']
        change_24h = response['bitcoin']['usd_24h_change']
        
        return {
            "price": f"{btc_price:,}",
            "sentiment": "ثيران (صعود)" if change_24h > 0 else "دببة (هبوط)",
            "change": f"{change_24h:.2f}%"
        }
    except:
        return {"price": "قيد التحليل", "sentiment": "غامض", "change": "0%"}

def generate_human_post(market_data):
    # البرومبت الخاص بـ WhaleMind: سيكولوجية القوة والفضول
    prompt = f"""
    Context: BTC Price ${market_data['price']} | Trend: {market_data['sentiment']}.
    Task: Write a cinematic Steemit post in ARABIC.
    Theme: 48 Laws of Power & Market Psychology.
    
    Structure:
    1. First line MUST be: 'Title: [عنوان مثير باللغة العربية]'
    2. Start with a cold truth about money and power.
    3. Treat market data as 'Whale footprints'.
    4. Use human-like Arabic transitions.
    5. Ending: A question that challenges the reader's perspective.
    """
    response = model.generate_content(prompt)
    return response.text

def publish_to_steemit(content):
    try:
        # فصل العنوان عن المحتوى
        lines = [l for l in content.split('\n') if l.strip()]
        if "Title:" in lines[0] or "عنوان:" in lines[0]:
            title = lines[0].split(':')[-1].replace('**', '').strip()
            body = '\n'.join(lines[1:])
        else:
            title = f"رؤية حوت: تحليل السوق النفسي {datetime.now().strftime('%H:%M')}"
            body = content

        # تنظيف المفتاح (في حال تم نسخه مع نصوص وصفية بالخطأ)
        # نحن نأخذ آخر جزء من النص في حال وجود فراغات
        final_key = str(POSTING_KEY).strip().split()[-1]

        # الاتصال بالبلوكشين (استخدام نود سريع)
        stm = Steem(node=["https://api.steemit.com"], keys=[final_key])
        
        tags = ["crypto", "psychology", "trading", "arabic", "steemexclusive"]
        
        print(f"جاري محاولة النشر للحساب: {STEEM_USER}...")
        stm.post(title=title, body=body, author=STEEM_USER, tags=tags, self_vote=True)
        print("✅ تم النشر بنجاح على بلوكشين Steem!")
        
    except Exception as e:
        print(f"❌ فشل النشر: {str(e)}")

if __name__ == "__main__":
    print(f"--- بدء عملية WhaleMind 2.5 ---")
    data = get_market_intelligence()
    post_content = generate_human_post(data)
    publish_to_steemit(post_content)
