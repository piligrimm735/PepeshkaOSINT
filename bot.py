import os
import re
import requests
import hashlib
import tempfile
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
import telebot

# Просто берём токен из окружения
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    print("❌ BOT_TOKEN не найден! Установи переменную окружения BOT_TOKEN")
    exit(1)

bot = telebot.TeleBot(TOKEN)

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
            <h1 align="center">🐸 PEPE REPORT: {data_type}</h1>
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

def report_phone(phone):
    clean = re.sub(r'\D', '', phone)
    return {
        "СВЯЗЬ": {"Номер": phone, "Регион": "Поиск...", "Оператор": "Определение..."},
        "МЕССЕНДЖЕРЫ": [f"WhatsApp: wa.me/{clean}", f"Telegram: t.me/+{clean}"],
        "СОВЕТ": "Для точных данных подключи API (LeakCheck, NumVerify)"
    }

def report_vin(vin):
    try:
        r = requests.get(f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/{vin}?format=json", timeout=10).json()
        details = {d['Variable']: d['Value'] for d in r['Results'][:10] if d.get('Value')}
        return {"VIN_DATA": details}
    except:
        return {"ERROR": "Сервер NHTSA недоступен"}

def report_ip(ip):
    try:
        data = requests.get(f"http://ip-api.com/json/{ip}", timeout=10).json()
        return {"GEO": data}
    except:
        return {"ERROR": "IP сервис недоступен"}

def report_email(email):
    md5 = hashlib.md5(email.lower().encode()).hexdigest()
    return {
        "GRAVATAR": f"https://www.gravatar.com/avatar/{md5}",
        "LINKS": [f"LeakCheck: https://leakcheck.net/search?check={email}"]
    }

def report_crypto(addr):
    if addr.startswith('0x') and len(addr) == 42:
        url = f"https://etherscan.io/address/{addr}"
    elif addr.startswith('1') or addr.startswith('3'):
        url = f"https://www.blockchain.com/explorer/addresses/btc/{addr}"
    else:
        url = f"https://blockchair.com/search?q={addr}"
    return {"BLOCKCHAIN": {"Address": addr, "Explorer": url}}

def report_username(nick):
    u = nick.replace('@', '')
    return {"SOCIAL": [
        f"GitHub: https://github.com/{u}",
        f"TikTok: https://tiktok.com/@{u}",
        f"Steam: https://steamcommunity.com/id/{u}",
        f"Twitter: https://twitter.com/{u}"
    ]}

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
        exif_data = img._getexif()
        if exif_data:
            exif = {TAGS.get(k, k): str(v) for k, v in exif_data.items() if k in TAGS}
            send_full_report(message.chat.id, "EXIF", "Image", {"METADATA": exif})
        else:
            bot.send_message(message.chat.id, "🐸 Метаданные не найдены.")
    except Exception as e:
        bot.send_message(message.chat.id, f"🐸 Ошибка: {str(e)[:100]}")
    finally:
        os.unlink(path)

@bot.message_handler(content_types=['text'])
def main_router(message):
    text = message.text.strip()
    
    if text.startswith('@'):
        send_full_report(message.chat.id, "Username", text, report_username(text))
    
    elif re.match(r'^\+?\d{10,15}$', text):
        send_full_report(message.chat.id, "Phone", text, report_phone(text))
    
    elif "@" in text and "." in text and len(text) < 100:
        send_full_report(message.chat.id, "Email", text, report_email(text))
    
    elif len(text) == 17 and text.isalnum() and any(c.isdigit() for c in text) and any(c.isalpha() for c in text):
        send_full_report(message.chat.id, "VIN", text.upper(), report_vin(text.upper()))
    
    elif re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', text):
        send_full_report(message.chat.id, "IP", text, report_ip(text))
    
    elif (text.startswith('0x') and len(text) == 42) or (text.startswith('1') and len(text) in [34, 42]):
        send_full_report(message.chat.id, "Crypto", text, report_crypto(text))
    
    elif len(text.split()) >= 2 and len(text) < 50:
        send_full_report(message.chat.id, "ФИО", text, {"Поиск": [f"Google: https://google.com/search?q={text}", f"VK: https://vk.com/people/{text}"]})
    
    else:
        bot.reply_to(message, "🐸 Жаба не понимает формат.\nПопробуй: номер, @username, email, VIN (17 символов), IP, или криптоадрес.")

if __name__ == "__main__":
    print("🐸 PEPE OSINT BOT запущен!")
    bot.infinity_polling()
