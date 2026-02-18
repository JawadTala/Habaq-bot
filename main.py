import os
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ── Config ──────────────────────────────────────────────────────────────
ACCESS_TOKEN   = os.environ.get("ACCESS_TOKEN", "")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID", "924145300793335")
VERIFY_TOKEN   = os.environ.get("VERIFY_TOKEN", "habaq_verify_2024")
API_URL = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

# ── Session storage (in-memory, resets on redeploy) ──────────────────────
sessions = {}  # { phone: { "step": ..., "ctx": {...} } }

# ── Bot Flows ────────────────────────────────────────────────────────────
def get_session(phone):
    if phone not in sessions:
        sessions[phone] = {"step": "welcome", "ctx": {}}
    return sessions[phone]

def set_session(phone, step, ctx=None):
    sessions[phone] = {"step": step, "ctx": ctx or {}}

def send_message(to, text):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    r = requests.post(API_URL, headers=headers, json=payload)
    print(f"[SEND] to={to} status={r.status_code} body={r.text}")
    return r

# ── Message Texts ────────────────────────────────────────────────────────
WELCOME = """أهلًا وسهلًا بك في *حبق للعطور – Habaq Perfumes* 🌿

لمساعدتك بسرعة، اختر رقم الخدمة:

1️⃣ طلب / شراء عطر
2️⃣ اقتراح عطر حسب ذوقك
3️⃣ الأسعار والأحجام
4️⃣ العطور المتوفرة اليوم
5️⃣ التوصيل والدفع
6️⃣ تتبّع طلب / تعديل طلب
7️⃣ التحدث مع موظف

اكتب 0 في أي وقت للعودة لهذه القائمة."""

FALLBACK = """لم أفهم اختيارك تمامًا 🙏
اكتب رقمًا من 1 إلى 7 أو اكتب *موظف*
اكتب 0 للعودة للقائمة الرئيسية."""

ORDER_CAT = """ممتاز ✅ هل العطر للـ:

1️⃣ رجال (M)
2️⃣ نساء (W)
3️⃣ يونيسكس (U)"""

ORDER_STRENGTH = """تحبّه يكون:

1️⃣ فواح وثابت قوي 🔥
2️⃣ متوازن يومي ⚖️
3️⃣ ناعم وخفيف 🌸"""

ORDER_SIZE = """اختر الحجم:

1️⃣ 30 ml
2️⃣ 50 ml
3️⃣ 100 ml"""

def order_confirm(ctx):
    return f"""تمام! ✅ ملخّص طلبك:

🗂 الفئة: *{ctx.get('category','—')}*
💨 القوة: *{ctx.get('strength','—')}*
📦 الحجم: *{ctx.get('size','—')}*

أرسل لي الآن:
1. اسم العطر أو اكتب *اقترح*
2. منطقتك / مدينتك
3. طريقة الاستلام: *توصيل* أو *استلام من نقطة*

اكتب 0 للقائمة الرئيسية."""

SUGGEST_SCENT = """خلّيني أقترح عليك بدقة 👌

تحب الروائح:
1️⃣ حلوة 🍬
2️⃣ منعشة 🍃
3️⃣ خشبية 🪵
4️⃣ شرقية 🔮"""

SUGGEST_OCCASION = """المناسبة:

1️⃣ دوام 💼
2️⃣ سهرات 🌙
3️⃣ يومي ☀️
4️⃣ هدية 🎁"""

def suggest_result(ctx):
    scent = ctx.get('scent','—')
    occasion = ctx.get('occasion','—')
    return f"""بناءً على ذوقك ({scent} – {occasion}) 🌿

أفضل 3 اقتراحات لك:

1️⃣ *Baccarat Rouge 540* – رقيّ استثنائي، دافئ وثابت
2️⃣ *Oud Ispahan – Dior* – عربي أصيل بلمسة فرنسية
3️⃣ *Black Orchid – TF* – غامض وجذّاب للسهرات

تحب نكمل الطلب؟ اكتب رقم العطر + الحجم
اكتب 0 للقائمة الرئيسية."""

PRICES = """📋 الأحجام المتوفرة: *30ml / 50ml / 100ml*

للاستفسار عن سعر محدد، اكتب:
اسم العطر + الحجم
مثال: Bleu de Chanel 50

اكتب 7 للتحدث مع موظف
اكتب 0 للقائمة الرئيسية."""

AVAILABLE = """المتوفر اليوم 🌿

👨 *Men:*
• Bleu de Chanel
• Sauvage – Dior
• Aventus – Creed

👩 *Women:*
• Miss Dior Blooming
• Coco Mademoiselle
• Light Blue – D&G

✨ *Unisex:*
• Baccarat Rouge 540
• Oud Wood – TF

لطلب أي عطر: اكتب 1
اكتب 0 للقائمة الرئيسية."""

DELIVERY = """🚚 *التوصيل:* بيروت، الضاحية، الجنوب، البقاع، الشمال
⏱ *زمن التوصيل:* 24–48 ساعة
💳 *الدفع:* نقدًا عند الاستلام / تحويل

لتأكيد التوصيل: أرسل المنطقة + أقرب نقطة دلالة
اكتب 1 لطلب عطر
اكتب 0 للقائمة الرئيسية."""

TRACK = """لإيجاد طلبك بسرعة، أرسل:
*رقم الطلب* أو *رقم الهاتف* المستخدم في الطلب.

للتعديل اكتب: تعديل + التعديل المطلوب
اكتب 7 للتحدث مع موظف
اكتب 0 للقائمة الرئيسية."""

AGENT = """حاضر ✅ سيتم تحويلك لموظف خدمة العملاء.

⏰ أوقات العمل: 9ص – 9م
📞 أو تواصل مباشرة: wa.me/96179336448

اكتب سؤالك الآن وسيردّ عليك أقرب وقت 🌿"""

# ── Process incoming message ─────────────────────────────────────────────
def process_message(phone, text):
    text = text.strip()
    lower = text.lower()
    session = get_session(phone)
    step = session["step"]
    ctx = session["ctx"].copy()

    # Global shortcuts
    if text == "0":
        set_session(phone, "welcome")
        return send_message(phone, WELCOME)
    if lower in ["موظف", "agent", "7"] and step not in ["agent"]:
        set_session(phone, "agent")
        return send_message(phone, AGENT)

    # ── Welcome ──
    if step == "welcome":
        if text == "1":
            set_session(phone, "order_cat", ctx)
            return send_message(phone, ORDER_CAT)
        elif text == "2":
            set_session(phone, "suggest_scent", ctx)
            return send_message(phone, SUGGEST_SCENT)
        elif text == "3":
            set_session(phone, "prices", ctx)
            return send_message(phone, PRICES)
        elif text == "4":
            set_session(phone, "available", ctx)
            return send_message(phone, AVAILABLE)
        elif text == "5":
            set_session(phone, "delivery", ctx)
            return send_message(phone, DELIVERY)
        elif text == "6":
            set_session(phone, "track", ctx)
            return send_message(phone, TRACK)
        elif text == "7":
            set_session(phone, "agent", ctx)
            return send_message(phone, AGENT)
        else:
            return send_message(phone, FALLBACK)

    # ── Order: Category ──
    elif step == "order_cat":
        cats = {"1": "رجال (M)", "2": "نساء (W)", "3": "يونيسكس (U)"}
        if text in cats:
            ctx["category"] = cats[text]
            set_session(phone, "order_strength", ctx)
            return send_message(phone, ORDER_STRENGTH)
        else:
            return send_message(phone, ORDER_CAT)

    # ── Order: Strength ──
    elif step == "order_strength":
        strengths = {"1": "فواح وثابت قوي 🔥", "2": "متوازن يومي ⚖️", "3": "ناعم وخفيف 🌸"}
        if text in strengths:
            ctx["strength"] = strengths[text]
            set_session(phone, "order_size", ctx)
            return send_message(phone, ORDER_SIZE)
        else:
            return send_message(phone, ORDER_STRENGTH)

    # ── Order: Size ──
    elif step == "order_size":
        sizes = {"1": "30 ml", "2": "50 ml", "3": "100 ml"}
        if text in sizes:
            ctx["size"] = sizes[text]
            set_session(phone, "order_confirm", ctx)
            return send_message(phone, order_confirm(ctx))
        else:
            return send_message(phone, ORDER_SIZE)

    # ── Order: Confirm (collecting free text) ──
    elif step == "order_confirm":
        if lower == "اقترح":
            set_session(phone, "suggest_scent", ctx)
            return send_message(phone, SUGGEST_SCENT)
        else:
            # Save whatever they typed as order details
            ctx["order_details"] = text
            set_session(phone, "order_done", ctx)
            msg = f"""✅ تم تسجيل طلبك بنجاح!\n\n📦 التفاصيل: {text}\n\nسنتواصل معك قريبًا لتأكيد الطلب والتوصيل 🌿\n\nاكتب 0 للقائمة الرئيسية."""
            return send_message(phone, msg)

    # ── Suggest: Scent ──
    elif step == "suggest_scent":
        scents = {"1": "حلوة 🍬", "2": "منعشة 🍃", "3": "خشبية 🪵", "4": "شرقية 🔮"}
        if text in scents:
            ctx["scent"] = scents[text]
            set_session(phone, "suggest_occasion", ctx)
            return send_message(phone, SUGGEST_OCCASION)
        else:
            return send_message(phone, SUGGEST_SCENT)

    # ── Suggest: Occasion ──
    elif step == "suggest_occasion":
        occasions = {"1": "دوام 💼", "2": "سهرات 🌙", "3": "يومي ☀️", "4": "هدية 🎁"}
        if text in occasions:
            ctx["occasion"] = occasions[text]
            set_session(phone, "suggest_result", ctx)
            return send_message(phone, suggest_result(ctx))
        else:
            return send_message(phone, SUGGEST_OCCASION)

    # ── Suggest: Result (collect order) ──
    elif step == "suggest_result":
        if text == "1":
            set_session(phone, "order_cat", ctx)
            return send_message(phone, ORDER_CAT)
        else:
            set_session(phone, "order_done", ctx)
            msg = f"""✅ ممتاز! سجّلنا اهتمامك بـ: *{text}*\n\nسيتواصل معك موظفنا لتأكيد التفاصيل والسعر 🌿\n\nاكتب 0 للقائمة الرئيسية."""
            return send_message(phone, msg)

    # ── Static steps ──
    elif step in ["prices", "available", "delivery", "track", "agent", "order_done"]:
        # Re-send welcome on any input from static pages
        if text in ["1","2","3","4","5","6"]:
            set_session(phone, "welcome")
            return process_message(phone, text)
        else:
            set_session(phone, "welcome")
            return send_message(phone, WELCOME)

    else:
        set_session(phone, "welcome")
        return send_message(phone, WELCOME)


# ── Webhook Routes ────────────────────────────────────────────────────────
@app.route("/webhook", methods=["GET"])
def verify():
    mode  = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("[WEBHOOK] Verified ✅")
        return challenge, 200
    return "Forbidden", 403


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("[INCOMING]", json.dumps(data, indent=2, ensure_ascii=False))
    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        if "messages" not in value:
            return jsonify({"status": "no message"}), 200

        message = value["messages"][0]
        phone = message["from"]
        msg_type = message.get("type", "")

        if msg_type == "text":
            text = message["text"]["body"]
            process_message(phone, text)
        else:
            send_message(phone, "أرسل رقمًا أو نصًا فقط 🙏\n\nاكتب 0 للقائمة الرئيسية.")

    except Exception as e:
        print(f"[ERROR] {e}")

    return jsonify({"status": "ok"}), 200


@app.route("/", methods=["GET"])
def home():
    return "🌿 Habaq Perfumes Bot is running!", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
