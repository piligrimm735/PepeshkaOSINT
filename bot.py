import telebot
import requests
import re
import hashlib
import os
import tempfile
import phonenumbers
from phonenumbers import geocoder, carrier
from urllib.parse import quote_plus
from datetime import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("BOTIK_TOKEN")

if not TOKEN:
    print("❌ КРИТИЧЕСКАЯ ОШИБКА: Токен BOT_TOKEN не найден в переменных окружения!")
    exit()

bot = telebot.TeleBot(TOKEN)

# ==========================================
# МОДУЛИ ПОИСКА (ВЕСЬ ФУНКЦИОНАЛ)
# ==========================================

def get_social_intel(query):
    """Поиск по никнейму во всех возможных сетях"""
    nick = query.lstrip('@')
    intel = {
        "🖼 АВАТАР": None,
        "🇷🇺 СОЦСЕТИ РФ": [
            f"https://vk.com/{nick}",
            f"https://ok.ru/search?st.query={nick}",
            f"https://habr.com/ru/users/{nick}/",
            f"https://picaso.biz/user/{nick}"
        ],
        "🚫 ЗАБЛОКИРОВАННЫЕ / GLOBAL": [
            f"https://www.instagram.com/{nick}/",
            f"https://twitter.com/{nick}",
            f"https://www.facebook.com/{nick}",
            f"https://www.linkedin.com/in/{nick}/",
            f"https://github.com/{nick}",
            f"https://www.pinterest.com/{nick}/"
        ],
        "📡 ИНДЕКСЫ": [
            f"https://www.google.com/search?q={quote_plus(nick)}",
            f"https://leakcheck.net/api/public?check={nick}&type=username"
        ]
    }
    try:
        r = requests.get(f"https://t.me/{nick}", timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(r.text, 'html.parser')
        img = soup.find('meta', property='og:image')
        if img: intel["🖼 АВАТАР"] = img.get('content')
    except: pass
    return intel

def get_phone_intel(phone):
    """Глубокий поиск по номеру"""
    clean = re.sub(r'\D', '', phone)
    formatted = "+" + clean
    res = {
        "📞 НОМЕР": formatted,
        "📍 ОПЕРАТОР/РЕГИОН": "Н/Д",
        "💬 МЕССЕНДЖЕРЫ": [f"https://wa.me/{clean}", f"https://t.me/{formatted}"],
        "💧 УТЕЧКИ (LEAKCHECK)": []
    }
    try:
        p = phonenumbers.parse(formatted)
        res["📍 ОПЕРАТОР/РЕГИОН"] = f"{geocoder.description_for_number(p, 'ru')}, {carrier.name_for_number(p, 'ru')}"
        lc = requests.get(f"https://leakcheck.net/api/public?check={clean}&type=phone", timeout=5).json()
        if lc.get('found'): res["💧 УТЕЧКИ (LEAKCHECK)"] = [str(s) for s in lc.get('sources', [])]
    except: pass
    return res

def get_car_intel(val):
    """Поиск по авто: VIN и Госномер"""
    val = val.upper().replace(' ', '')
    res = {"🚗 ОБЪЕКТ": val}
    if len(val) == 17:
        try:
            d = requests.get(f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvalues/{val}?format=json").json()
            i = d.get('Results', [{}])[0]
            res["📋 ДАННЫЕ VIN"] = {"Марка": i.get('Make'), "Модель": i.get('Model'), "Год": i.get('ModelYear'), "Страна": i.get('PlantCountry')}
        except: pass
    else:
        res["📸 ФОТО (НОМЕРОГРАМ)"] = f"https://nomerogram.ru/s/{val}/"
        res["🔍 ПРОВЕРКИ"] = [f"https://vincode.ru/gosnomer/{val}", f"https://проверки.гибдд.рф"]
    return res

def get_email_intel(email):
    """Поиск по почте"""
    h = hashlib.md5(email.lower().encode()).hexdigest()
    res = {
        "📧 EMAIL": email,
        "🖼 GRAVATAR": f"https://www.gravatar.com/avatar/{h}?s=400&d=404",
        "💧 УТЕЧКИ": []
    }
    try:
        lc = requests.get(f"https://leakcheck.net/api/public?check={email}&type=email").json()
        if lc.get('found'): res["💧 УТЕЧКИ"] = [str(s) for s in lc.get('sources', [])]
    except: pass
    return res

def get_net_intel(val):
    """IP и Домены"""
    if re.match(r'^\d', val):
        try:
            d = requests.get(f"http://ip-api.com/json/{val}").json()
            return {"🌐 IP": val, "📍 GEO": f"{d.get('country')}, {d.get('city')}", "🏢 ПРОВАЙДЕР": d.get('isp')}
        except: return {"🌐 IP": val, "❌": "Ошибка"}
    return {"🌍 ДОМЕН": val, "🔍 DNS": f"https://dns.google/resolve?name={val}"}

# ==========================================
# ВИЗУАЛИЗАЦИЯ (АГРЕССИВНЫЙ HTML)
# ==========================================

def generate_html_report(title, data):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    # Используем двойные {{ }} для CSS, чтобы f-строка не ломалась
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset='UTF-8'>
        <style>
            body {{ background: #050805; color: #00ff66; font-family: monospace; padding: 20px; }}
            .report {{ max-width: 850px; margin: auto; border: 2px solid #00ff66; background: #0a0d0a; box-shadow: 0 0 20px #00ff66; position: relative; overflow: hidden; }}
            .scanline {{ width: 100%; height: 2px; background: rgba(0, 255, 102, 0.3); position: absolute; animation: scan 3s linear infinite; }}
            @keyframes scan {{ 0% {{ top: 0; }} 100% {{ top: 100%; }} }}
            .header {{ background: #00ff66; color: #000; padding: 15px; text-align: center; font-weight: bold; letter-spacing: 3px; }}
            .card {{ margin: 15px; border: 1px solid #1a331a; background: #0e110e; padding: 15px; border-radius: 5px; }}
            .photo {{ max-width: 250px; border: 1px solid #00ff66; filter: sepia(1) hue-rotate(90deg); transition: 0.3s; margin-bottom: 10px; }}
            .photo:hover {{ filter: none; }}
            a {{ color: #fff; text-decoration: none; border-bottom: 1px solid #00ff66; font-size: 0.9em; }}
            a:hover {{ background: #00ff66; color: #000; }}
            .row {{ display: flex; justify-content: space-between; border-bottom: 1px solid #1a331a; padding: 5px 0; }}
        </style>
    </head>
    <body>
        <div class="report">
            <div class="scanline"></div>
            <div class="header"><h1>PEPE OSINT TERMINAL v3.0</h1></div>
            <p style="text-align:center">ОБЪЕКТ: {title} | {timestamp}</p>
            <div class="content">
    """
    for sec, val in data.items():
        html += f"<div class='card'><h3>> {sec}</h3>"
        if isinstance(val, str) and ('.jpg' in val or '.png' in val or 'gravatar' in val or 'image' in val):
            html += f"<img src='{val}' class='photo' onerror='this.style.display=\"none\"'>"
        elif isinstance(val, dict):
            for k, v in val.items(): html += f"<div class='row'><b>{k}:</b> <span>{v}</span></div>"
        elif isinstance(val, list):
            for link in val: html += f"<div>• <a href='{link}' target='_blank'>{link}</a></div>"
        else:
            if str(val).startswith('http'): html += f"<a href='{val}'>{val}</a>"
            else: html += f"<div>{val}</div>"
        html += "</div>"
    
    html += "</div><div style='text-align:center; padding:10px; color:#004411;'>[ SYSTEM_STABLE ]</div></div></body></html>"
    return html

# ==========================================
# ОБРАБОТЧИКИ (ЛОГИКА БОТА)
# ==========================================

def send_intel(chat_id, title, data):
    code = generate_html_report(title, data)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(code)
        p = f.name
    with open(p, 'rb') as f:
        bot.send_document(chat_id, f, caption=f"🐸 PepeOSINT: {title}")
    os.unlink(p)

@bot.message_handler(commands=['start'])
def welcome(m):
    bot.reply_to(m, "🐸 **PepeOSINT Terminal v3.0**\n\nОтправь любые данные:\n- @никнейм\n- Номер телефона\n- Email\n- ФИО\n- VIN или Госномер\n- IP-адрес")

@bot.message_handler(content_types=['text'])
def main_handler(m):
    t = m.text.strip()
    try:
        if t.startswith('@'): 
            send_intel(m.chat.id, t, get_social_intel(t))
        elif re.match(r'^\+?\d{10,15}$', t): 
            send_intel(m.chat.id, t, get_phone_intel(t))
        elif "@" in t: 
            send_intel(m.chat.id, t, get_email_intel(t))
        elif len(t) == 17 or re.match(r'^[А-Я]\d{3}[А-Я]{2}\d{2,3}$', t.upper()): 
            send_intel(m.chat.id, t.upper(), get_car_intel(t))
        elif re.match(r'^\d{1,3}\.', t) or ('.' in t and ' ' not in t):
            send_intel(m.chat.id, t, get_net_intel(t))
        elif len(t.split()) >= 2:
            send_intel(m.chat.id, t, {"👤 ФИО": t, "🔎 ПОИСК": [f"https://vk.com/search?c[q]={quote_plus(t)}", f"https://www.google.com/search?q={quote_plus('intitle:'+t)}"]})
        else:
            bot.reply_to(m, "🐸 Неизвестный формат данных.")
    except Exception as e:
        bot.reply_to(m, f"❌ Ошибка системы: {e}")

if __name__ == "__main__":
    print("🐸 PepeOSINT Master Edition запущен...")
    bot.infinity_polling()
