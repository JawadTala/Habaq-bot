# 🌿 Habaq Perfumes – WhatsApp Bot

Automated WhatsApp bot for Habaq Perfumes using Meta Cloud API + Flask.

## Deploy on Render (Free)

1. Upload this folder to GitHub (new repo)
2. Go to render.com → New Web Service
3. Connect your GitHub repo
4. Set these Environment Variables:
   - ACCESS_TOKEN = your Meta access token
   - PHONE_NUMBER_ID = 924145300793335
   - VERIFY_TOKEN = habaq_verify_2024
5. Deploy!

## Connect to Meta Webhook

After deploy, copy your Render URL (e.g. https://habaq-bot.onrender.com)

In Meta Developer Console:
- Webhook URL: https://your-render-url.onrender.com/webhook
- Verify Token: habaq_verify_2024

## Bot Flows
1. طلب / شراء عطر
2. اقتراح عطر حسب الذوق
3. الأسعار والأحجام
4. المتوفر اليوم
5. التوصيل والدفع
6. تتبّع طلب
7. موظف
