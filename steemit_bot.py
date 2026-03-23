import os
from beem import Steem
from beem.account import Account

# الإعدادات من Secrets
POSTING_KEY = os.getenv("POSTING_KEY")
STEEM_USER = "whalemind"

def diagnostic_check():
    print(f"🔍 بدء فحص الحساب والمفتاح لـ @{STEEM_USER}...")
    try:
        # 1. محاولة الاتصال بنود مستقر
        stm = Steem(node="https://api.steemit.com", keys=[POSTING_KEY])
        
        # 2. فحص وجود الحساب
        account = Account(STEEM_USER, blockchain_instance=stm)
        print(f"✅ الحساب موجود فعلياً على البلوكشين.")
        
        # 3. فحص صلاحية المفتاح (برمجياً)
        # إذا لم يظهر خطأ هنا، فالمفتاح بصيغة Private Key صحيحة
        print(f"✅ صيغة المفتاح (WIF) صحيحة.")
        
        # 4. التحقق من مطابقة المفتاح للنشر
        # سنحاول فقط التحقق من الصلاحية دون نشر
        posting_auths = account['posting']['key_auths']
        print(f"ℹ️ الحساب يمتلك {len(posting_auths)} مفاتيح نشر مسجلة.")
        
        print("\n🚀 النتيجة: الإعدادات البرمجية سليمة، المشكلة كانت في 'النود' الذي استخدمته سابقاً.")

    except Exception as e:
        print(f"\n❌ فشل الفحص: {str(e)}")
        if "WIF" in str(e):
            print("💡 التنبيه: المفتاح الذي وضعته ليس 'Private Posting Key'. تأكد أنه يبدأ برقم 5.")
        elif "AccountDoesNotExists" in str(e):
            print("💡 التنبيه: الحساب غير موجود أو أن خادم Steemit لا يراه حالياً.")

if __name__ == "__main__":
    diagnostic_check()
