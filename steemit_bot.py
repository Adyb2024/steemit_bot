import os
import requests
import google.generativeai as genai
from beem import Steem
from datetime import datetime

# --- [1] الإعدادات وجلب المفاتيح ---
STEEM_USER = "whalemind"
POSTING_KEY = os.getenv("POSTING_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_KEY")

# إعداد Gemini 2.5 Flash
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

def get_market_data():
    """جلب بيانات البيتكوين"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
        r = requests.get(url, timeout=15)
        data = r.json()['bitcoin']
        return {"price": f"{data['usd']:,}", "change": f"{data['usd_24h_change']:+.2f}%"}
    except:
        return {"price": "71,000", "change": "متذبذب"}

def generate_content(market):
    """توليد المقال بأسلوب حيتان المال"""
    prompt = f"""
    اكتب مقالاً بليغاً بالعربية لـ Steemit عن سعر البيتكوين الحالي (${market['price']}) وتغيره ({market['change']}).
    استخدم أسلوباً يحلل سيكولوجية الجشع والخوف، واذكر صراع الحيتان في السوق.
    اجعل العنوان يبدأ بـ 'Title:' واختم بـ 5 وسوم (tags).
    """
    response = model.generate_content(prompt)
    return response.text

def publish_final(content):
    """النشر المباشر دون فحص الحساب لتجنب AttributeError"""
    try:
        lines = content.split('\n')
        title = lines[0].replace('Title:', '').strip()
        body = '\n'.join(lines[1:])
        
        # استخدام نودز قوية ومجربة
        nodes = ["https://api.steemit.com", "https://anyx.io"]
        stm = Steem(node=nodes, keys=[POSTING_KEY])
        
        print(f"🚀 جاري دفع المقال إلى @{STEEM_USER}...")
        stm.post(
            title=title[:255],
            body=body + f"\n\n---\n*تم التوليد بواسطة WhaleMind (Gemini 2.5 Flash) | {datetime.now().date()}*",
            author=STEEM_USER,
            tags=["crypto", "arabic", "bitcoin", "gemini25", "trading"],
            self_vote=True
        )
        return True
    except Exception as e:
        print(f"❌ فشل النشر: {e}")
        return False

if __name__ == "__main__":
    print(f"🤖 تشغيل WhaleMind v2.7 لـ {STEEM_USER}")
    market = get_market_data()
    content = generate_content(market)
    if publish_final(content):
        print("✅ تم النشر بنجاح باهر!")
