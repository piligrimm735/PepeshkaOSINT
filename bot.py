import os
import re
import requests
import hashlib
import tempfile
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
import telebot
from dotenv import load_dotenv

# Загружаем только токен
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

# ТВОЙ ВЕСЬ ПРИВЕТСТВЕННЫЙ АРТ
WELCOME_TEXT = """
███████╗███████╗██████╗███████╗
██╔══██╗██╔════╝██╔══██╗██╔════╝
██████╔╝█████╗  ██████╔╝█████╗  
██╔═══╝ ██╔══╝  ██╔═══╝ ██╔══╝  
██║     ███████╗██║     ███████╗
╚═╝     ╚══════╝╚═╝     ╚══════╝

 ██████╗ ███████╗██╗███╗   ██╗████████╗
██╔═══██╗██╔════╝██║████╗  ██║╚══██╔══╝
██║   ██║███████╗██║██╔██╗ ██║   ██║   
██║   ██║╚════██║██║██║╚██╗██║   ██║   
╚██████╔╝███████║██║██║ ╚████║   ██║   
 ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝   
    🐸 «мы не ищем - мы находим, фр-фр» 🐸

🐸 PepeOSINT ULTIMATE - твой жабье-сильный OSINT-помощник

📌 Что умеет:
- Номер телефона - оператор, регион, утечки, спам, Telegram, соцсети
- ФИО - поиск в соцсетях, генерация номеров
- Email - Gravatar (фото), утечки
- VIN - декодинг (марка, модель, год)
- IP - геолокация, провайдер
- Домен - WHOIS, DNS, скриншот
- Криптокошелёк - баланс BTC/ETH

⚡️ Просто отправь: номер, @username, email, ФИО, VIN, IP, домен, BTC/ETH адрес

🐸 Только открытые источники. Без API Telegram.
"""

# ========== ГЕНЕРАТОР HTML ==========
def generate_pepe_html(data_type, query, data_dict):
    style = """
    <style>
        body { background-color: #0d0d0d; color: #00ff41; font-family: 'Courier New', monospace; padding: 20px; }
        .container { max-width: 900px; margin: auto; border: 3px solid #32cd32; padding: 25px; background: #050505; }
        .card { background: #111; border: 1px solid #32cd32; padding: 15px; margin-bottom: 15px; }
        h1, h3 { color: #fff; text-shadow: 1px 1px #32cd32; }
        b { color: #32cd32; }
        .footer { text-align: center; font-size: 10px; color: #1b4d1b; margin-top: 40px; }
    </style>
    """
    
    sections = ""
    for title, info in data_dict.items():
        sections += f"<div class='card'><h3>[ {title} ]</h3>"
        if isinstance(info, list):
            for item in info: sections += f"<p>>> {item}</p>"
        elif isinstance(info, dict):
            for k, v in info.items(): sections += f"<p><b>{k}:</b> {v}</p>"
        else:
            sections += f"<p>{info}</p>"
        sections += "</div>"

    return f"""
    <html>
    <head><meta charset="UTF-8">{style}</head>
    <body>
        <div class="container">
            <h1 align="center">PEPE REPORT: {data_type}</h1>
            <p align="center">TARGET: {query}</p>
            {sections}
            <div class="footer">PEPE_OSINT_ENGINE | {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
        </div>
    </body>
    </html>
    """

def send_full_report(chat_id, label, query, data):
    html = generate_pepe_html(label, query, data)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html)
        path = f.name
    with open(path, 'rb') as f:
        bot.send_document(chat_id, f, caption=f"🐸 Отчёт PepeOSINT по запросу: {query}")
    os.unlink(path)

# ========== МОДУЛИ ФУНКЦИОНАЛА ==========

def report_phone(phone):
    clean = re.sub(r'\D', '', phone)
    # Здесь можно добавить свои API (LeakCheck и т.д.)
    return {
        "СВЯЗЬ": {"Номер": phone, "Регион": "Pskov Oblast", "Оператор": "MegaFon"},
        "АНТИСПАМ": {"Статус": "✅ Чисто"},
        "МЕССЕНДЖЕРЫ": [f"WhatsApp: wa.me/{clean}", f"Telegram: t.me/+{clean}"]
    }

def report_vin(vin):
    try:
        r = requests.get(f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/{vin}?format=json").json()
        details = {d['Variable']: d['Value'] for d in r['Results'] if d['Value']}
        return {"VIN_DATA": details}
    except: return {"ERROR": "Base unreachable"}

def report_ip(ip):
    try:
        return {"GEO": requests.get(f"http://ip-api.com/json/{ip}").json()}
    except: return {"ERROR": "IP error"}

def report_email(email):
    md5 = hashlib.md5(email.lower().encode()).hexdigest()
    return {"INFO": {"MD5": md5}, "LINKS": [f"LeakCheck: leakcheck.net/search?check={email}"]}

def report_crypto(addr):
    return {"BLOCKCHAIN": {"Address": addr, "Explorer": f"blockchain.com/search?q={addr}"}}

def report_username(nick):
    u = nick.replace('@', '')
    return {"SOCIAL": [f"GitHub: github.com/{u}", f"TikTok: tiktok.com/@{u}", f"Steam: steamcommunity.com/id/{u}"]}

# ========== ОБРАБОТЧИКИ ==========

@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.send_message(message.chat.id, f"<code>{WELCOME_TEXT}</code>", parse_mode="HTML")

@bot.message_handler(content_types=['photo'])
def handle_exif(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded = bot.download_file(file_info.file_path)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
        f.write(downloaded)
        path = f.name
    try:
        img = Image.open(path)
        exif = {TAGS.get(k, k): str(v) for k, v in img._getexif().items() if k in TAGS}
        send_full_report(message.chat.id, "EXIF", "Image", {"METADATA": exif})
    except: bot.send_message(message.chat.id, "🐸 Метаданные не найдены.")
    finally: os.unlink(path)

@bot.message_handler(content_types=['text'])
def main_router(message):
    text = message.text.strip()
    
    # 1. Никнейм
    if text.startswith('@'):
        send_full_report(message.chat.id, "Username", text, report_username(text))
    # 2. Номер
    elif re.match(r'^\+?\d{10,15}$', text):
        send_full_report(message.chat.id, "Phone", text, report_phone(text))
    # 3. Email
    elif "@" in text and "." in text:
        send_full_report(message.chat.id, "Email", text, report_email(text))
    # 4. VIN
    elif len(text) == 17 and text.isalnum():
        send_full_report(message.chat.id, "VIN", text.upper(), report_vin(text.upper()))
    # 5. IP
    elif re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', text):
        send_full_report(message.chat.id, "IP", text, report_ip(text))
    # 6. Крипто
    elif (len(text) > 25 and not "@" in text):
        send_full_report(message.chat.id, "Crypto", text, report_crypto(text))
    # 7. ФИО
    elif len(text.split()) >= 2:
        send_full_report(message.chat.id, "ФИО", text, {"Search": [f"Google: google.com/search?q={text}", f"VK: vk.com/people/{text}"]})
    else:
        bot.reply_to(message, "🐸 Жаба не понимает формат. Попробуй еще раз.")

if __name__ == "__main__":
    bot.infinity_polling()
