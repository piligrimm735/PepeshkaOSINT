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

# === НАСТРОЙКА ===
TOKEN = "BOT_TOKEN" 
bot = telebot.TeleBot(TOKEN)

# --- 1. МОДУЛЬ СОЦСЕТЕЙ (РФ + Заблокированные) ---
def search_social_all(query):
    nick = query.lstrip('@')
    res = {
        "🖼 PHOTO": None,
        "🇷🇺 RUSSIAN NETS": [
            f"https://vk.com/{nick}",
            f"https://ok.ru/search?st.query={nick}",
            f"https://habr.com/ru/users/{nick}/"
        ],
        "🚫 BANNED / GLOBAL": [
            f"https://www.instagram.com/{nick}/",
            f"https://www.facebook.com/{nick}",
            f"https://twitter.com/{nick}",
            f"https://www.linkedin.com/in/{nick}/",
            f"https://github.com/{nick}",
            f"https://www.pinterest.com/{nick}/"
        ]
    }
    # Пытаемся вытянуть превью из TG/VK
    try:
        r = requests.get(f"https://t.me/{nick}", timeout=5)
        soup = BeautifulSoup(r.text, 'html.parser')
        img = soup.find('meta', property='og:image')
        if img: res["🖼 PHOTO"] = img.get('content')
    except: pass
    return res

# --- 2. МОДУЛЬ МАШИН (VIN + Госномер) ---
def search_car_all(val):
    val = val.upper().replace(' ', '')
    res = {"🚗 TARGET": val}
    if len(val) == 17: # VIN
        try:
            d = requests.get(f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvalues/{val}?format=json").json()
            info = d.get('Results', [{}])[0]
            res["📋 INFO"] = {"Brand": info.get('Make'), "Model": info.get('Model'), "Year": info.get('ModelYear')}
            res["🔗 LINKS"] = [f"https://проверки.гибдд.рф/checking/auto/history?vin={val}"]
        except: pass
    else: # Госномер РФ
        res["📸 NOMEROGRAM"] = f"https://nomerogram.ru/s/{val}/"
        res["🔗 CHECK"] = [f"https://vincode.ru/gosnomer/{val}", f"https://www.google.com/search?q={quote_plus(val)}"]
    return res

# --- 3. МОДУЛЬ СЕТИ (IP + Домен) ---
def search_net_all(val):
    if re.match(r'^\d', val): # IP
        try:
            d = requests.get(f"http://ip-api.com/json/{val}").json()
            return {"🌐 IP": val, "📍 GEO": f"{d.get('country')}, {d.get('city')}", "🏢 ISP": d.get('isp')}
        except: return {"🌐 IP": val, "❌": "Error"}
    else: # Domain
        return {"🌍 DOMAIN": val, "🔍 SEARCH": [f"https://dns.google/resolve?name={val}&type=A"]}

# --- 4. МОДУЛЬ EMAIL + УТЕЧКИ ---
def search_email_all(email):
    h = hashlib.md5(email.lower().encode()).hexdigest()
    res = {
        "📧 EMAIL": email,
        "🖼 GRAVATAR": f"https://www.gravatar.com/avatar/{h}?s=400&d=404",
        "💧 LEAKS": []
    }
    try:
        lc = requests.get(f"https://leakcheck.net/api/public?check={email}&type=email").json()
        if lc.get('found'): res["💧 LEAKS"] = [str(s) for s in lc.get('sources', [])]
    except: pass
    return res

# --- 5. МОДУЛЬ ФИО ---
def search_fio_all(fio):
    return {
        "👤 FULL NAME": fio,
        "🇷🇺 RU SEARCH": [f"https://vk.com/search?c[q]={quote_plus(fio)}", f"https://ok.ru/search?st.query={quote_plus(fio)}"],
        "🌎 GLOBAL": [f"https://www.google.com/search?q={quote_plus('site:facebook.com ' + fio)}"],
        "📄 DOCUMENTS": [f"https://www.google.com/search?q={quote_plus(fio + ' filetype:pdf')}"]
    }

# --- 🎨 ТВОЙ ВИЗУАЛ ГЕНЕРАТОРА ОТЧЕТОВ ---
def generate_html(title, data):
    html = f"""
    <html><head><meta charset='UTF-8'>
    <style>
        body {{ background: #0a0a0a; color: #00ff66; font-family: 'Consolas', monospace; padding: 30px; }}
        .report-box {{ border: 2px solid #00ff66; padding: 25px; border-radius: 20px; box-shadow: 0 0 20px #004411; background: #0d0d0d; }}
        .card {{ background: #111; border: 1px solid #00ff66; padding: 15px; margin: 15px 0; border-radius: 12px; }}
        .header {{ text-align: center; border-bottom: 2px solid #00ff66; margin-bottom: 20px; padding-bottom: 10px; }}
        .photo {{ max-width: 250px; border: 2px solid #00ff66; border-radius: 15px; margin-bottom: 15px; display: block; }}
        a {{ color: #ffffff; text-decoration: none; font-weight: bold; }}
        a:hover {{ background: #00ff66; color: #000; }}
        .row {{ display: flex; justify-content: space-between; border-bottom: 1px solid #1a331a; padding: 5px 0; }}
        .label {{ color: #00ff66; font-weight: bold; }}
    </style></head><body>
    <div class='report-box'>
        <div class='header'>
            <h1>🐸 PepeOSINT INTELLIGENCE</h1>
            <p>OBJECT: {title} | DATE: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
    """
    for sec, val in data.items():
        html += f"<div class='card'><h3>[+] {sec}</h3>"
        if isinstance(val, str) and ('.jpg' in val or '.png' in val or 'gravatar' in val or 'image' in val):
            html += f"<img src='{val}' class='photo' onerror='this.style.display=\"none\"'>"
        elif isinstance(val, dict):
            for k, v in val.items(): html += f"<div class='row'><span class='label'>{k}:</span><span>{v}</span></div>"
        elif isinstance(val, list):
            for i in val: html += f"<div>• <a href='{i}' target='_blank'>{i}</a></div>"
        else: html += f"<div>{val}</div>"
        html += "</div>"
    
    html += "<p align='center' style='color:#004411;'>End of Report</p></div></body></html>"
    return html

def send_res(chat_id, title, data):
    code = generate_html(title, data)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(code); p = f.name
    with open(p, 'rb') as f:
        bot.send_document(chat_id, f, caption=f"🐸 PepeOSINT: {title}")
    os.unlink(p)

# --- ОБРАБОТЧИК ---
@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "🐸 **PepeOSINT ONLINE**\nОтправь: Номер, Email, @Username, ФИО, IP, Домен, VIN или Госномер.")

@bot.message_handler(content_types=['text'])
def handle(m):
    t = m.text.strip()
    if t.startswith('@'): send_res(m.chat.id, t, search_social_all(t))
    elif re.match(r'^\+?\d{10,15}$', t): 
        c = re.sub(r'\D', '', t)
        res = {"📞 PHONE": f"+{c}", "📍 REGION": "Checking...", "💧 LEAKS": []}
        try:
            p = phonenumbers.parse("+"+c)
            res["📍 REGION"] = f"{geocoder.description_for_number(p, 'ru')}, {carrier.name_for_number(p, 'ru')}"
            lc = requests.get(f"https://leakcheck.net/api/public?check={c}&type=phone").json()
            if lc.get('found'): res["💧 LEAKS"] = [str(s) for s in lc.get('sources', [])]
        except: pass
        send_res(m.chat.id, t, res)
    elif "@" in t: send_res(m.chat.id, t, search_email_all(t))
    elif re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', t) or '.' in t: send_res(m.chat.id, t, search_net_all(t))
    elif len(t) == 17 or re.match(r'^[А-Я]\d{3}[А-Я]{2}\d{2,3}$', t.upper()): send_res(m.chat.id, t.upper(), search_car_all(t))
    elif len(t.split()) >= 2: send_res(m.chat.id, t, search_fio_all(t))
    else: bot.reply_to(m, "🐸 Error: Data format not recognized.")

if __name__ == "__main__":
    bot.infinity_polling()
