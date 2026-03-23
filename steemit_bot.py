import os
import requests
import random
import google.generativeai as genai
from beem import Steem
from datetime import datetime

# --- [1] الإعدادات وجلب المفاتيح ---
STEEM_USER = "whalemind"
POSTING_KEY = os.getenv("POSTING_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_KEY")

# إعداد Gemini 2.5 Flash (نحافظ على هذا الموديل كما طلبنا سابقاً لسرعته وكفاءته)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

def get_dynamic_market_data():
    """جلب بيانات عملة يتم اختيارها عشوائياً لتجنب تكرار المواضيع"""
    coins = {
        "bitcoin": "البيتكوين", 
        "ethereum": "الإيثريوم", 
        "solana": "سولانا", 
        "binancecoin": "بينانس كوين"
    }
    selected_coin_id = random.choice(list(coins.keys()))
    coin_name = coins[selected_coin_id]

    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={selected_coin_id}&vs_currencies=usd&include_24hr_change=true"
        r = requests.get(url, timeout=15)
        data = r.json()[selected_coin_id]
        return {
            "id": selected_coin_id,
            "name": coin_name,
            "price": f"{data['usd']:,}",
            "change": f"{data['usd_24h_change']:+.2f}%"
        }
    except Exception as e:
        print(f"⚠️ خطأ في جلب بيانات {coin_name}: {e}")
        return {"id": "bitcoin", "name": "البيتكوين", "price": "غير متاح", "change": "متذبذب"}

def generate_content(market):
    """توليد المقال بأسلوب سينمائي وفلسفي متغير"""
    
    # قائمة من الزوايا النفسية لضمان عدم تكرار فكرة المقال أبداً
    themes = [
        "قانون القوة: اسحق عدوك تماماً (وكيف تطبقه الحيتان لتصفية المتداولين الصغار)",
        "وهم الخيار: كيف توهم الأسواق المالية صغار المستثمرين بأنهم يمتلكون السيطرة",
        "تأثير الهالة: الانخداع بالشموع الخضراء المتتالية والسقوط في الفخ",
        "هندسة الفضول: كيف تصنع الأخبار المالية شراكاً لاصطياد السيولة",
        "قانون القوة: خطط للوصول إلى النهاية (صراع الصبر بين الاستثمار والمضاربة)"
    ]
    selected_theme = random.choice(themes)

    prompt = f"""
    أنت محلل أسواق خبير وكاتب 'سينمائي' غامض تكتب لحساب 'WhaleMind' على منصة Steemit.
    
    مهمتك اليوم: كتابة مقال بليغ وعميق عن عملة {market['name']} التي سعرها الآن ${market['price']} وتغيرها {market['change']}.
    
    الزاوية النفسية والفلسفية الإجبارية للمقال اليوم: "{selected_theme}"
    
    شروط صارمة لعدم التكرار والاحترافية:
    1. يُمنع منعاً باتاً استخدام مقدمات ترحيبية تقليدية (مثل: أهلاً بكم، مرحباً أيها المستثمرون، في هذا المقال). ادخل في صلب المشهد المظلم مباشرة.
    2. غير هيكل المقال تماماً. استخدم تساؤلات فلسفية، واقتباسات عميقة، وتجنب السرد النمطي.
    3. اجعل الأسلوب 'Cinematic' (سينمائي يصور السوق كساحة معركة نفسية أو رقعة شطرنج معقدة).
    4. اجعل السطر الأول يبدأ بـ 'Title:' متبوعاً بعنوان جذاب، غامض، وغير مكرر.
    5. اختم المقال بسؤال مفتوح يثير الفضول والجدل لدفع القراء للتعليق.
    """
    
    print(f"🧠 جاري توليد أفكار حول: {market['name']} بناءً على زاوية: {selected_theme}")
    
    # استخدام إعدادات Temperature أعلى قليلاً لزيادة الإبداع ومنع التكرار
    response = model.generate_content(
        prompt,
        generation_config={"temperature": 0.85}
    )
    return response.text

def publish_final(content, coin_id):
    """النشر المباشر مع وسوم (Tags) متغيرة"""
    try:
        lines = content.split('\n')
        title = lines[0].replace('Title:', '').replace('**', '').strip()
        body = '\n'.join(lines[1:])
        
        nodes = ["https://api.steemit.com", "https://anyx.io", "https://api.steemitdev.com"]
        stm = Steem(node=nodes, keys=[POSTING_KEY])
        
        # وسوم ديناميكية تتغير حسب العملة المختارة
        dynamic_tags = ["crypto", "arabic", "whalemind", coin_id, "psychology"]
        
        print(f"🚀 جاري دفع المقال الجديد بعنوان: '{title}' إلى @{STEEM_USER}...")
        
        stm.post(
            title=title[:255],
            body=body + f"\n\n---\n*تم التوليد بواسطة WhaleMind (Gemini 2.5 Flash) | {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
            author=STEEM_USER,
            tags=dynamic_tags,
            self_vote=True
        )
        return True
    except Exception as e:
        print(f"❌ فشل النشر: {e}")
        return False

if __name__ == "__main__":
    print(f"🤖 تشغيل WhaleMind v3.0 (النسخة الديناميكية) لـ {STEEM_USER}")
    
    # 1. جلب بيانات عملة عشوائية
    market_data = get_dynamic_market_data()
    print(f"📊 تم اختيار هدف اليوم: {market_data['name']} بسعر {market_data['price']}")
    
    # 2. توليد المحتوى بالثيم الجديد
    content = generate_content(market_data)
    
    # 3. النشر
    if publish_final(content, market_data['id']):
        print("✅ تم النشر بنجاح باهر وبمحتوى جديد كلياً!")
