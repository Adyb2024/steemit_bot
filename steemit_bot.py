import os
import requests
import random
import google.generativeai as genai
from beem import Steem
from datetime import datetime

# --- [1] Configuration & Keys ---
STEEM_USER = "whalemind"
POSTING_KEY = os.getenv("POSTING_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_KEY")

# Initializing Gemini (Gemini 2.5 Flash is highly stable for your account)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

def get_dynamic_market_data():
    """Fetching real-time data for different coins to avoid repetition"""
    coins = {
        "bitcoin": "Bitcoin", 
        "ethereum": "Ethereum", 
        "solana": "Solana", 
        "binancecoin": "BNB"
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
        print(f"⚠️ Market Data Error: {e}")
        return {"id": "bitcoin", "name": "Bitcoin", "price": "71,200", "change": "Volatile"}

def generate_content(market):
    """Generating viral, cinematic, and psychological English content with Emojis"""
    
    # Psychological themes to ensure 100% unique posts every time
    themes = [
        "The Law of Power: Crush Your Fear 🦈 (How whales liquidate the weak hands)",
        "The Illusion of Choice: Are you a player or just liquidity? 🕸️",
        "The Halo Effect: Why green candles blind the masses 🕯️✨",
        "Curiosity Engineering: Decoding the silence before the storm 🌊📈",
        "The Law of Power: Plan all the way to the end 🏁 (The ultimate patience game)"
    ]
    selected_theme = random.choice(themes)

    prompt = f"""
    You are an elite market strategist writing for 'WhaleMind' on Steemit. 
    Target: Global Crypto Investors.
    
    Current Asset: {market['name']}
    Price: ${market['price']} 
    24h Change: {market['change']}
    Theme: "{selected_theme}"
    
    Visual & Content Strategy:
    1. Start the Title with a striking emoji. Use a 'Viral' and 'Mysterious' headline.
    2. Use emojis (🐋, 💎, 📊, ⚡, 🌑) to make the text pop and keep users engaged.
    3. NO intro greetings. Dive straight into a dark, cinematic financial analysis.
    4. Structure the article with Bold headers, Quotes, and Emoji-bullet points.
    5. The style should be deep, philosophical, and focus on Whale Psychology.
    6. Start the first line with 'Title:' followed by the post title.
    7. End with a sharp, provocative question to maximize comments.
    """
    
    print(f"🧠 Generating insights for {market['name']} using theme: {selected_theme}")
    
    # High temperature for maximum creativity and diverse emoji usage
    response = model.generate_content(
        prompt,
        generation_config={"temperature": 0.9}
    )
    return response.text

def publish_final(content, coin_id):
    """Publishing to Steemit with a professional, global footer"""
    try:
        lines = content.split('\n')
        # Cleaning the title from formatting artifacts
        title = lines[0].replace('Title:', '').replace('**', '').replace('"', '').strip()
        body = '\n'.join(lines[1:])
        
        # High-stability Nodes
        nodes = ["https://api.steemit.com", "https://anyx.io", "https://api.steemitdev.com"]
        stm = Steem(node=nodes, keys=[POSTING_KEY])
        
        # Viral global tags
        global_tags = ["crypto", "bitcoin", "trading", "psychology", coin_id]
        
        # Professional Global Footer (No AI Mentioned)
        custom_footer = f"""
<center>

***
#### 👁️ Published by: [WhaleMind]
*The Digital Chessboard | {datetime.now().strftime('%Y-%m-%d')}*
***

</center>

> **⚠️ Legal Disclaimer:** This content is a philosophical and analytical view of market movements. It is not financial advice. Always remember, the digital chessboard is high-risk.
"""
        
        print(f"🚀 Deploying Global Post: '{title}' to @{STEEM_USER}...")
        
        stm.post(
            title=title[:255],
            body=body + custom_footer,
            author=STEEM_USER,
            tags=global_tags,
            self_vote=True
        )
        return True
    except Exception as e:
        print(f"❌ Publishing Failed: {e}")
        return False

if __name__ == "__main__":
    print(f"🤖 WhaleMind Global v3.5 is active for @{STEEM_USER}")
    
    # 1. Fetch random asset data
    market_data = get_dynamic_market_data()
    
    # 2. Generate cinematic English content
    content = generate_content(market_data)
    
    # 3. Final Push to Blockchain
    if publish_final(content, market_data['id']):
        print("✅ SUCCESS: Global post is live with visual attraction!")
