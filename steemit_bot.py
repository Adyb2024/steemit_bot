import os
import requests
import google.generativeai as genai
from beem import Steem
from datetime import datetime

# --- [1] جلب الإعدادات من GitHub Secrets ---
# تأكد من إضافة هذه الأسماء في إعدادات Secrets في جيت هوب
STEEM_USER = os.getenv("STEEM_USER")
POSTING_KEY = os.getenv("POSTING_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_KEY")

# إعداد ذكاء Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def get_market_intelligence():
    try:
        # جلب بيانات حية للمؤشرات
        price_res = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT").json()
        fng_res = requests.get("https://api.alternative.me/fng/").json()
        
        data = {
            "price": price_res['price'],
            "sentiment": fng_res['data'][0]['value_classification'],
            "score": fng_res['data'][0]['value']
        }
        return data
    except:
        return {"price": "Market Data unavailable", "sentiment": "Uncertain", "score": "50"}

def generate_human_post(market_data):
    # الـ Prompt المصمم لهندسة الفضول وسيكولوجية القوة
    prompt = f"""
    Context: BTC is at ${market_data['price']} and market sentiment is {market_data['sentiment']}.
    Task: Write a deep, cinematic Steemit post as a 'Shadow Analyst'. 
    
    Structure:
    1. Start with a provocative thought about human greed or power (48 Laws of Power style).
    2. Discuss the data not as numbers, but as 'Whale behavior'.
    3. Use human-like transitions: 'To be fair', 'The real kicker is', 'I’ve seen this before'.
    4. NO AI CLICHES: No 'In conclusion' or 'Exciting times'.
    5. Formatting: Use Markdown with bold headers and blockquotes.
    6. Ending: Ask a controversial question to trigger comments.
    
    Tags: #crypto #steemexclusive #psychology #trading #arbitrage #finance
    """
    response = model.generate_content(prompt)
    return response.text

def publish_to_steemit(content):
    try:
        lines = content.split('\n')
        title = lines[0].replace('Title: ', '').replace('**', '').strip()
        body = '\n'.join(lines[1:])
        
        # توقيع احترافي (Cyber Signature)
        footer = f"\n\n---\n*Written by Cyber-Intelligence | {datetime.now().strftime('%Y-%m-%d')}*"
        
        stm = Steem(keys=[POSTING_KEY])
        tags = ["crypto", "steemexclusive", "psychology", "trading", "arbitrage"]
        
        stm.post(title=title, body=body + footer, author=STEEM_USER, tags=tags, self_vote=True)
        print(f"Success: {title}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    data = get_market_intelligence()
    post_content = generate_human_post(data)
    publish_to_steemit(post_content)
