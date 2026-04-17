import telebot
import requests
import re
import hashlib
import os
import random
import tempfile
from urllib.parse import quote_plus
from datetime import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# ========== 📞 МОДУЛЬ: НОМЕР (ТВОЯ ЛОГИКА + API) ==========
def get_phone_intel(phone):
    clean = re.sub(r'\D', '', phone)
    res = {
        "number": clean,
        "formatted": f"+{clean}",
        "spam": "Чисто или нет данных",
        "leaks": [],
        "links": [f"https://wa.me/{clean}", f"https://t.me/+{clean}"]
    }
    # Проверка спама (как в твоем коде)
    try:
        resp = requests.get(f"https://api.phonespam.info/phone/{clean}", timeout=5).json()
        if resp.get('spam'): res["spam"] = "🚩 ОБНАРУЖЕН СПАМ / МОШЕННИКИ"
        if resp.get('carrier'): res["operator"] = resp.get('carrier')
    except: pass
    
    # Утечки
    try:
        lc = requests.get(f"https://leakcheck.net/api/public?check={clean}&type=phone", timeout=5).json()
        if lc.get('found'): res["leaks"] = [str(s) for s in lc.get('sources', [])]
    except: pass
    return res

# ========== 👤 МОДУЛЬ: ФИО (ТВОЯ ГЕНЕРАЦИЯ) ==========
def get_fio_intel(fullname):
    res = {
        "ФИО": fullname,
        "🔍 СОЦСЕТИ": {
            "VK": f"https://vk.com/search?c[q]={quote_plus(fullname)}",
            "OK": f"https://ok.ru/search?st.query={quote_plus(fullname)}",
            "FB": f"https://www.facebook.com/search/people/?q={quote_plus(fullname)}"
        },
        "🎲 ВЕРОЯТНЫЕ НОМЕРА": []
    }
    # Твой алгоритм генерации номеров
    codes = ['910','911','916','920','921','925','926','977','978','999']
    random.seed(hash(fullname) % 1000)
    for _ in range(5):
        c = random.choice(codes)
        suffix = ''.join(str(random.randint(0,9)) for _ in range(7))
        res["🎲 ВЕРОЯТНЫЕ НОМЕРА"].append(f"+7 ({c}) {suffix[:3]}-{suffix[3:5]}-{suffix[5:7]}")
    return res

# ========== 📧 МОДУЛЬ: EMAIL (ТВОЙ DNS ПОИСК) ==========
def get_email_intel(email):
    h = hashlib.md5(email.lower().encode()).hexdigest()
    domain = email.split('@')[-1]
    res = {
        "email": email,
        "gravatar": f"https://www.gravatar.com/avatar/{h}?s=400&d=mp",
        "mx_records": [],
        "leaks": []
    }
    # Твой поиск MX-записей через Google
    try:
        dns = requests.get(f"https://dns.google/resolve?name={domain}&type=MX").json()
        res["mx_records"] = [ans['data'].split()[-1] for ans in dns.get('Answer', []) if 'data' in ans]
    except: pass
    
    try:
        lc = requests.get(f"https://leakcheck.net/api/public?check={email}&type=email").json()
        if lc.get('found'): res["leaks"] = [str(s) for s in lc.get('sources', [])]
    except: pass
    return res

# ========== 🎨 ВЕРНУЛ ПОЛНЫЙ ВИЗУАЛ (HTML) ==========
def generate_html(title, data):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    html = f"""
    <html><head><meta charset='UTF-8'><style>
        body {{ background: #050a05; color: #0f6; font-family: 'Courier New', monospace; padding: 20px; }}
        .box {{ max-width: 800px; margin: auto; border: 2px solid #0f6; background: #080f08; box-shadow: 0 0 20px #040; position: relative; }}
        .header {{ background: #0f6; color: #000; padding: 15px; text-align: center; font-weight: bold; font-size: 20px; }}
        .card {{ border-left: 4px solid #0f6; margin: 20px; padding: 15px; background: #0c140c; }}
        .photo {{ max-width: 150px; border: 2px solid #0f6; margin-bottom: 10px; border-radius: 10px; }}
        a {{ color: #fff; text-decoration: none; border-bottom: 1px solid #0f6; }}
        .row {{ display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px dashed #1a331a; }}
    </style></head><body>
    <div class='box'>
        <div class='header'>🐸 PEPE OSINT: МЫ НЕ ИЩЕМ — МЫ НАХОДИМ, ФР-ФР</div>
        <div style='text-align:center; padding:10px;'>ЦЕЛЬ: {title} | {ts}</div>
    """
    for sec, val in data.items():
        html += f"<div class='card'><h3>[+] {sec}</h3>"
        if sec == "gravatar" or sec == "photo":
            html += f"<img src='{val}' class='photo'>"
        elif isinstance(val, dict):
            for k, v in val.items(): html += f"<div class='row'><b>{k}:</b> <a href='{v}'>{v}</a></div>"
        elif isinstance(val, list):
            for i in val: html += f"<div>• {i}</div>"
        else: html += f"<div>{val}</div>"
        html += "</div>"
    return html + "</div></body></html>"

# ========== ОБРАБОТЧИКИ (ФУНКЦИОНАЛ) ==========
def send_report(chat_id, title, data):
    code = generate_html(title, data)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(code)
        p = f.name
    with open(p, 'rb') as f:
        bot.send_document(chat_id, f, caption=f"🐸 Отчет PepeOSINT: {title}")
    os.unlink(p)

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "🐸 PepeOSINT FULL активен. Жду данные (Номер, ФИО, Почта, @Ник).")

@bot.message_handler(content_types=['text'])
def handle(m):
    t = m.text.strip()
    # Логика определения типа данных
    if t.startswith('@'):
        nick = t.lstrip('@')
        send_report(m.chat.id, t, {"Username": t, "Links": [f"https://t.me/{nick}", f"https://vk.com/{nick}"]})
    elif re.match(r'^\+?\d{10,15}$', t):
        send_report(m.chat.id, t, get_phone_intel(t))
    elif "@" in t:
        send_report(m.chat.id, t, get_email_intel(t))
    elif len(t.split()) >= 2:
        send_report(m.chat.id, t, get_fio_intel(t))
    else:
        bot.reply_to(m, "🐸 Не понял формат. Дай номер, ФИО или почту.")

bot.infinity_polling()
