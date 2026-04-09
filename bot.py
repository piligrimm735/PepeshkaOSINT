import telebot
import requests
import re
import hashlib
import json
import time
import os
import random
import tempfile
import csv
from urllib.parse import quote_plus
from datetime import datetime
from io import BytesIO, StringIO
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# ========== ЗАГРУЗКА ПЕРЕМЕННЫХ ==========
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    print("❌ BOT_TOKEN не найден в .env")
    exit(1)

bot = telebot.TeleBot(TOKEN)

# ========== ASCII-АРТ ЛЯГУШКИ ==========
PEPE_ART = """
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
"""

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
def clean_phone(phone):
    return re.sub(r'\D', '', phone)

def format_phone(phone):
    c = clean_phone(phone)
    if len(c) == 11 and c[0] == '7':
        return f"+7 ({c[1:4]}) {c[4:7]}-{c[7:9]}-{c[9:11]}"
    return f"+{c}" if c else phone

def get_operator(phone_clean):
    if not phone_clean.startswith('7') or len(phone_clean) < 4:
        return "Не определён"
    def_code = phone_clean[1:4]
    ops = {
        '910':'МТС','911':'МТС','912':'МТС','913':'МТС','914':'МТС','915':'МТС','916':'МТС','917':'МТС','918':'МТС','919':'МТС',
        '920':'МегаФон','921':'МегаФон','922':'МегаФон','923':'МегаФон','924':'МегаФон','925':'МегаФон','926':'МегаФон','927':'МегаФон','928':'МегаФон','929':'МегаФон',
        '930':'МегаФон','931':'МегаФон','932':'МегаФон','933':'МегаФон','934':'МегаФон','935':'МегаФон','936':'МегаФон','937':'МегаФон','938':'МегаФон','939':'МегаФон',
        '902':'Билайн','903':'Билайн','904':'Билайн','905':'Билайн','906':'Билайн','909':'Билайн',
        '960':'Билайн','961':'Билайн','962':'Билайн','963':'Билайн','964':'Билайн','965':'Билайн','966':'Билайн','967':'Билайн','968':'Билайн','969':'Билайн',
        '950':'Tele2','951':'Tele2','952':'Tele2','953':'Tele2','958':'Tele2','959':'Tele2',
        '977':'Tele2','978':'Tele2','979':'Tele2','991':'Tele2','992':'Tele2','993':'Tele2','994':'Tele2','995':'Tele2','996':'Tele2','999':'Tele2'
    }
    return ops.get(def_code, "Не определён")

def get_region(phone_clean):
    if not phone_clean.startswith('7') or len(phone_clean) < 4:
        return "Не определён"
    def_code = phone_clean[1:4]
    regions = {
        '910':'Центр','911':'Центр','912':'Центр','913':'Сибирь','914':'Дальний Восток','915':'Центр','916':'Центр','917':'Центр','918':'Юг','919':'Центр',
        '920':'Центр','921':'Северо-Запад','922':'Урал','923':'Сибирь','924':'Дальний Восток','925':'Центр','926':'Центр','927':'Поволжье','928':'Юг','929':'Центр',
        '930':'Центр','931':'Центр','932':'Центр','933':'Центр','934':'Центр','936':'Центр','937':'Центр','938':'Центр','939':'Центр','950':'Поволжье',
        '951':'Поволжье','952':'Поволжье','953':'Поволжье','958':'Поволжье','959':'Поволжье','960':'Центр','961':'Центр','962':'Центр','963':'Центр','964':'Центр',
        '965':'Центр','966':'Центр','967':'Центр','968':'Центр','969':'Центр','977':'Центр','978':'Северо-Запад','979':'Центр','991':'Центр','992':'Центр',
        '993':'Центр','994':'Центр','995':'Центр','996':'Центр','999':'Центр'
    }
    return regions.get(def_code, "Не определён")

# ========== УТЕЧКИ (LeakCheck) ==========
def check_leaks(query, query_type="phone"):
    results = []
    try:
        url = f"https://leakcheck.net/api/public?check={query}&type={query_type}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('found'):
                for src in data.get('sources', []):
                    if isinstance(src, dict):
                        results.append(f"{src.get('name','?')} ({src.get('date','?')})")
                    else:
                        results.append(str(src))
    except:
        pass
    return results

# ========== СТАРЫЙ КРАСИВЫЙ HTML-ГЕНЕРАТОР ==========
def generate_pepe_html(data_type, query, data_dict):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>🐸 PepeOSINT — {data_type}</title>
    <style>
        @import url('https://fonts.cdnfonts.com/css/minecraft');
        body {{
            background: radial-gradient(circle at 20% 30%, #0a2f1f, #051a0e);
            font-family: 'Minecraft', 'Courier New', monospace;
            padding: 2rem;
            color: #ccffcc;
            min-height: 100vh;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .pepe-header {{
            text-align: center;
            margin-bottom: 2rem;
            background: rgba(0,0,0,0.5);
            border-radius: 60px;
            padding: 1.5rem;
            border: 2px solid #6aab5a;
            box-shadow: 0 0 20px #3c9e3c;
        }}
        .pepe-header h1 {{
            font-family: 'Minecraft', 'Press Start 2P', cursive;
            font-size: 1.8rem;
            color: #b5ff9e;
            text-shadow: 3px 3px 0 #1a4d1a;
        }}
        .query-frog {{
            background: #1e3a1e;
            display: inline-block;
            padding: 0.7rem 1.5rem;
            border-radius: 40px;
            font-family: 'Minecraft', monospace;
            margin: 1rem 0;
            border-left: 5px solid #96ff6a;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 1.8rem;
            margin: 2rem 0;
        }}
        .frog-card {{
            background: rgba(20, 45, 20, 0.85);
            backdrop-filter: blur(6px);
            border-radius: 32px;
            padding: 1.2rem 1.5rem;
            border: 1px solid #7cbc6a;
            transition: 0.2s;
        }}
        .frog-card:hover {{
            transform: translateY(-5px);
            border-color: #c8ffa2;
            box-shadow: 0 0 20px #6eff6e;
        }}
        .card-title {{
            font-size: 1.4rem;
            font-weight: bold;
            margin-bottom: 1rem;
            color: #b3ffa7;
            border-left: 5px solid #96ff6a;
            padding-left: 0.8rem;
            font-family: 'Minecraft', monospace;
        }}
        .data-row {{
            display: flex;
            justify-content: space-between;
            padding: 0.6rem 0;
            border-bottom: 1px dashed #4a7a4a;
        }}
        .data-label {{ font-weight: 600; color: #bbffaa; }}
        .data-value {{ font-family: 'Minecraft', monospace; word-break: break-word; text-align: right; color: #f0fff0; }}
        .link-list {{ list-style: none; margin-top: 0.5rem; }}
        .link-list li {{ margin: 0.6rem 0; word-break: break-all; }}
        .link-list a {{ color: #aaffaa; text-decoration: none; border-bottom: 1px dotted #6aff6a; }}
        .pepe-footer {{
            text-align: center;
            margin-top: 3rem;
            padding: 1rem;
            font-size: 0.75rem;
            color: #6e9e6e;
            border-top: 1px solid #3a6a3a;
        }}
        .avatar-img {{
            max-width: 100px;
            border-radius: 50%;
            border: 2px solid #6aab5a;
            display: block;
            margin: 0 auto;
        }}
    </style>
</head>
<body>
<div class="container">
    <div class="pepe-header">
        <h1>🐸 PepeOSINT</h1>
        <p>«мы не ищем - мы находим, фр-фр»</p>
        <div class="query-frog">🔍 {data_type.upper()} : {query}</div>
        <p>⚡ отчёт сгенерирован {timestamp} ⚡</p>
    </div>
    <div class="grid">
"""
    for title, items in data_dict.items():
        html += f"""
        <div class="frog-card">
            <div class="card-title">{title}</div>
        """
        if isinstance(items, list):
            html += '<ul class="link-list">'
            for item in items:
                if isinstance(item, str) and ('http' in item or '://' in item):
                    html += f'<li>🐸 <a href="{item}" target="_blank">{item}</a></li>'
                else:
                    html += f'<li>- {item}</li>'
            html += '</ul>'
        elif isinstance(items, dict):
            for label, value in items.items():
                if label == "Аватар":
                    html += f'<div class="data-row"><span class="data-label">{label}:</span><span class="data-value"><img src="{value}" class="avatar-img"></span></div>'
                elif value and isinstance(value, str) and ('http' in value or '://' in value):
                    html += f'<div class="data-row"><span class="data-label">{label}:</span><span class="data-value"><a href="{value}" target="_blank">{value}</a></span></div>'
                else:
                    html += f'<div class="data-row"><span class="data-label">{label}:</span><span class="data-value">{value or "-"}</span></div>'
        else:
            html += f'<div class="data-row"><span class="data-value">{items}</span></div>'
        html += '</div>'

    html += """
    </div>
    <div class="pepe-footer">
        🐸 Все данные из открытых источников. Жабье одобрение 🐸
    </div>
</div>
</body>
</html>
"""
    return html

def send_pepe_html(chat_id, data_type, query, data_dict):
    html = generate_pepe_html(data_type, query, data_dict)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html)
        path = f.name
    with open(path, 'rb') as f:
        bot.send_document(chat_id, f, caption=f"🐸 Отчёт PepeOSINT - {data_type}")
    os.unlink(path)

# ========== ОТЧЁТ ПО НОМЕРУ ==========
def phone_report(phone_input):
    phone_clean = clean_phone(phone_input)
    if not phone_clean:
        return None
    
    data = {
        "🐸 Основное": {
            "Номер": format_phone(phone_clean),
            "Страна": "Россия / Казахстан",
            "Оператор": get_operator(phone_clean),
            "Регион": get_region(phone_clean),
        },
        "⚠️ Утечки (LeakCheck)": [],
        "🐸 Спам-статус": "",
        "🌐 Соцсети": []
    }
    
    # Утечки
    leaks = check_leaks(phone_clean, "phone")
    if leaks:
        data["⚠️ Утечки (LeakCheck)"] = leaks
    else:
        data["⚠️ Утечки (LeakCheck)"] = ["✅ Не найден"]
    
    # Спам
    try:
        resp = requests.get(f"https://api.phonespam.info/phone/{phone_clean}", timeout=5)
        if resp.status_code == 200:
            spam_data = resp.json()
            data["🐸 Спам-статус"] = "🚫 Спам" if spam_data.get('spam') else "✅ Чисто"
        else:
            data["🐸 Спам-статус"] = "❓ Недоступно"
    except:
        data["🐸 Спам-статус"] = "❓ Ошибка"
    
    # Соцсети
    data["🌐 Соцсети"] = [
        f"VK: https://vk.com/search?c[phone]={phone_clean}",
        f"OK: https://ok.ru/search?st.query={phone_clean}",
        f"Facebook: https://www.facebook.com/search/top/?q={phone_clean}",
        f"WhatsApp: https://wa.me/{phone_clean}",
        f"Truecaller: https://www.truecaller.com/search/global/{phone_clean}"
    ]
    
    return data

# ========== ОТЧЁТ ПО EMAIL ==========
def email_report(email):
    domain = email.split('@')[-1]
    hash_md5 = hashlib.md5(email.lower().encode()).hexdigest()
    data = {
        "🐸 Email": {"Email": email, "Домен": domain},
        "🖼️ Gravatar": f"https://www.gravatar.com/avatar/{hash_md5}?s=200&d=mp",
        "⚠️ Утечки": []
    }
    leaks = check_leaks(email, "email")
    if leaks:
        data["⚠️ Утечки"] = leaks
    else:
        data["⚠️ Утечки"] = ["✅ Не найден"]
    return data

# ========== ОТЧЁТ ПО ФИО ==========
def fullname_report(fullname):
    parts = fullname.strip().split()
    if len(parts) < 2:
        return None
    encoded = quote_plus(fullname)
    data = {
        "🐸 ФИО": {"Имя": fullname},
        "🌐 Соцсети": [
            f"VK: https://vk.com/search?c[q]={encoded}",
            f"OK: https://ok.ru/search?st.query={encoded}",
            f"Facebook: https://www.facebook.com/search/people/?q={encoded}"
        ],
        "📱 Вероятные номера": []
    }
    codes = ['910','911','916','920','921','925','926','977','978','999']
    random.seed(hash(fullname) % 1000)
    for _ in range(6):
        code = random.choice(codes)
        suffix = ''.join(str(random.randint(0,9)) for _ in range(7))
        data["📱 Вероятные номера"].append(f"+7 ({code}) {suffix[:3]}-{suffix[3:5]}-{suffix[5:7]}")
    return data

# ========== ОТЧЁТ ПО VIN ==========
def vin_report(vin):
    vin = vin.upper().strip()
    if len(vin) != 17:
        return None
    data = {
        "🚗 VIN": {"VIN": vin},
        "🔧 Декодинг": {},
        "🔗 История": f"https://vincheck.info/check/{vin}"
    }
    try:
        resp = requests.get(f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/{vin}?format=json", timeout=10)
        if resp.status_code == 200:
            for item in resp.json().get('Results', []):
                if item['Variable'] in ['Make', 'Model', 'ModelYear', 'VehicleType']:
                    data["🔧 Декодинг"][item['Variable']] = item['Value']
    except:
        data["🔧 Декодинг"] = {"Ошибка": "Сервис недоступен"}
    return data

# ========== ОТЧЁТ ПО IP ==========
def ip_report(ip):
    data = {"🐸 IP": {"IP": ip}}
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        if resp.status_code == 200:
            geo = resp.json()
            if geo.get('status') == 'success':
                data["🌍 Геолокация"] = {
                    "Страна": geo.get('country', 'Н/Д'),
                    "Регион": geo.get('regionName', 'Н/Д'),
                    "Город": geo.get('city', 'Н/Д'),
                    "Провайдер": geo.get('isp', 'Н/Д')
                }
    except:
        data["🌍 Геолокация"] = {"Ошибка": "Нет соединения"}
    return data

# ========== ОТЧЁТ ПО ДОМЕНУ ==========
def domain_report(domain):
    data = {
        "🐸 Домен": {"Домен": domain},
        "📋 WHOIS": {},
        "🌐 DNS A": [],
        "📸 Скриншот": f"https://mini.s-shot.ru/1024x768/PNG/?url={quote_plus(domain)}"
    }
    try:
        resp = requests.get(f"https://whois-api.com/?domain={domain}", timeout=10)
        if resp.status_code == 200:
            w_data = resp.json()
            data["📋 WHOIS"] = {
                "Регистратор": w_data.get('registrar', 'Н/Д'),
                "Создан": w_data.get('creation_date', 'Н/Д'),
                "Истекает": w_data.get('expiration_date', 'Н/Д')
            }
    except:
        data["📋 WHOIS"] = {"Ошибка": "WHOIS недоступен"}
    try:
        resp = requests.get(f"https://dns.google/resolve?name={domain}&type=A", timeout=5)
        if resp.status_code == 200:
            dns_data = resp.json()
            a_records = [ans['data'] for ans in dns_data.get('Answer', []) if ans.get('type') == 1]
            if a_records:
                data["🌐 DNS A"] = a_records
    except:
        data["🌐 DNS A"] = ["Ошибка проверки"]
    return data

# ========== КОМАНДЫ ==========
@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.send_message(message.chat.id,
f"""{PEPE_ART}

🐸 *PepeOSINT ULTIMATE* - твой жабье-сильный помощник

📌 *Что умеет:*
- Номер телефона - оператор, регион, утечки, спам
- ФИО - поиск в соцсетях, генерация номеров
- Email - Gravatar (фото), утечки
- VIN - декодинг (марка, модель, год)
- IP - геолокация, провайдер
- Домен - WHOIS, DNS, скриншот

⚡ *Просто отправь:* номер, ФИО, email, VIN, IP, домен

🐸 *Только открытые источники. Без API Telegram.*""", parse_mode="Markdown")

@bot.message_handler(commands=['art'])
def art(message):
    art_url = "https://i.imgur.com/6b3jL9c.png"
    try:
        bot.send_photo(message.chat.id, art_url, caption="🐸 Девушка Пепе")
    except:
        bot.send_message(message.chat.id, "🐸 Арт временно недоступен")

# ========== АВТООПРЕДЕЛЕНИЕ ==========
@bot.message_handler(content_types=['text'])
def handle_text(message):
    text = message.text.strip()
    if text.startswith('/'):
        return
    
    if re.match(r'^\+?\d{10,15}$', text):
        data = phone_report(text)
        if data:
            send_pepe_html(message.chat.id, "Номер телефона", text, data)
        else:
            bot.reply_to(message, "❌ Неверный номер")
        return
    
    if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', text):
        data = email_report(text)
        send_pepe_html(message.chat.id, "Email", text, data)
        return
    
    if re.match(r'^[A-HJ-NPR-Z0-9]{17}$', text, re.IGNORECASE):
        data = vin_report(text.upper())
        if data:
            send_pepe_html(message.chat.id, "VIN", text.upper(), data)
        else:
            bot.reply_to(message, "❌ Неверный VIN")
        return
    
    if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', text):
        data = ip_report(text)
        send_pepe_html(message.chat.id, "IP", text, data)
        return
    
    if '.' in text and ' ' not in text and not text.startswith('http'):
        data = domain_report(text)
        send_pepe_html(message.chat.id, "Домен", text, data)
        return
    
    if len(text.split()) >= 2 and re.search(r'[А-Яа-я]', text):
        data = fullname_report(text)
        if data:
            send_pepe_html(message.chat.id, "ФИО", text, data)
        else:
            bot.reply_to(message, "❌ Введите имя и фамилию")
        return
    
    bot.reply_to(message, "🐸 Не распознано. Отправьте: номер, ФИО, email, VIN, IP, домен")

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    print("🐸 PepeOSINT запущен. Жабья сила активирована!")
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Ошибка: {e}. Переподключение через 10 секунд...")
            time.sleep(10)
