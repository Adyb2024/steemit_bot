import os
import requests
import random
import google.generativeai as genai
from beem import Steem
from datetime import datetime

# --- [1] Configuration ---
STEEM_USER = "whalemind"
POSTING_KEY = os.getenv("POSTING_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

def get_dynamic_market_data():
    """Fetching data with Sentiment Analysis Logic"""
    coins = {"bitcoin": "Bitcoin", "ethereum": "Ethereum", "solana": "Solana", "binancecoin": "BNB"}
    selected_coin_id = random.choice(list(coins.keys()))
    
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={selected_coin_id}&vs_currencies=usd&include_24hr_change=true"
        r = requests.get(url, timeout=15)
        raw_data = r.json()[selected_coin_id]
        
        change = raw_data['usd_24h_change']
        # --- Logic: Sentiment Analysis ---
        if change > 3:
            sentiment = "🔥 Bullish Euphoria (Greed)"
        elif change < -3:
            sentiment = "🩸 Bearish Panic (Fear)"
        else:
            sentiment = "⚖️ Neutral Accumulation (Sideways)"
            
        return {
            "id": selected_coin_id,
            "name": coins[selected_coin_id],
            "price": f"{raw_data['usd']:,}",
            "change": f"{change:+.2f}%",
            "sentiment": sentiment,
            "raw_price": raw_data['usd']
        }
    except:
        return {"id": "bitcoin", "name": "Bitcoin", "price": "71,000", "change": "0.00%", "sentiment": "⚖️ Neutral", "raw_price": 71000}

def generate_content(market):
    """Predictive Prompting & Visual Structure Generation"""
    
    themes = [
        "The Law of Power: Control the Narrative 🦈",
        "Market Manipulation: Reading Whale Footprints 🐋",
        "The Psychology of Support and Resistance 📉"
    ]
    
    # تحسين الـ Prompt ليكون تحليلياً وتوقعيّاً
    prompt = f"""
    Act as an Elite Wall Street Crypto Analyst for 'WhaleMind'.
    Asset: {market['name']} | Current Price: ${market['price']} | 24h Change: {market['change']}
    Market Sentiment: {market['sentiment']}
    Theme: {random.choice(themes)}

    Structure Instructions (Visual Structure):
    1. START with a viral Title including emojis.
    2. DATA TABLE: Create a clear Markdown table for [Price, Change, Sentiment].
    3. PREDICTIVE ANALYSIS: Based on ${market['price']}, predict the next 'Support' and 'Resistance' levels.
    4. CONTENT: Write a deep, cinematic psychological analysis (English). NO AI greetings.
    5. EMOJIS: Use them to highlight professional points (🚀, 💎, 📉, 🐋).
    6. CALL TO ACTION: End with a provocative question to drive comments.
    """
    
    response = model.generate_content(prompt, generation_config={"temperature": 0.85})
    return response.text

def publish_final(content, coin_id):
    """Publishing with Global Professional Footer"""
    try:
        lines = content.split('\n')
        title = lines[0].replace('Title:', '').replace('**', '').replace('"', '').strip()
        body = '\n'.join(lines[1:])
        
        nodes = ["https://api.steemit.com", "https://anyx.io"]
        stm = Steem(node=nodes, keys=[POSTING_KEY])
        
        custom_footer = f"""
<center>

***
#### 👁️ Analysis by: [WhaleMind Global]
*The Digital Chessboard | {datetime.now().strftime('%Y-%m-%d')}*
***
</center>

> **⚠️ Disclaimer:** This is psychological market mapping, not financial advice. Trade at your own risk. 🐋
"""
        
        print(f"🚀 Deploying Analytical Post: '{title}'...")
        stm.post(
            title=title[:255],
            body=body + custom_footer,
            author=STEEM_USER,
            tags=["crypto", "trading", "bitcoin", "psychology", coin_id],
            self_vote=True
        )
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    market_data = get_dynamic_market_data()
    content = generate_content(market_data)
    if publish_final(content, market_data['id']):
        print("✅ Success! Professional Analysis is Live.")
