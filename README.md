# SigmaECC Telegram Bot 🤖

A simple Telegram bot to collect name and phone number from users and notify the admin.

## Features:
- Collect name and phone number
- Validate phone numbers (must start with 09 and be 11 digits)
- Save user data to CSV file
- Notify admin on each new registration
- Admin commands:
  - /users → show number of registered users
  - /export → get CSV file

## Deployment
1. Add your bot token in `sigmaecc_bot_admin.py`:
   Replace `PASTE_YOUR_BOT_TOKEN_HERE` with your actual token from BotFather.
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Run the bot:
```bash
python sigmaecc_bot_admin.py
```

## License
MIT
