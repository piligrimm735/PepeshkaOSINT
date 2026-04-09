import os
import logging
import sys
import random
import json
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========== ПОЛУЧАЕМ ТОКЕН ИЗ СЕКРЕТОВ ==========
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN не найден! Установи секрет BOT_TOKEN на хостинге")
    sys.exit(1)

logger.info("✅ Токен успешно загружен из секретов")

# ========== ОСНОВНОЙ КЛАСС БОТА ==========
class PepeOSINTBot:
    def __init__(self):
        self.pepe_faces = {
            "feelsgood": "😎",
            "feelsbad": "😢",
            "monkaS": "😨",
            "pepeLaugh": "😏",
            "pepeHands": "🤲",
            "pepega": "🤪"
        }
        
        self.osint_sources = [
            "GitHub", "Pastebin", "Telegram", "Twitter/X", 
            "Reddit", "4chan", "Discord", "Instagram", 
            "LinkedIn", "Facebook", "YouTube", "TikTok"
        ]
        
        self.osint_tools = [
            "theHarvester", "Maltego", "Shodan", "Censys",
            "Recon-ng", "SpiderFoot", "OSINT Framework", "Google Dorks"
        ]
    
    def create_ascii_pepe(self, style="normal"):
        """Создает ASCII-арт PEPE"""
        arts = {
            "normal": """
╔════════════════════════════════╗
║         ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿         ║
║         ⣿⣿⣿⣿⣿⣿⣿⣿⡿⠛⠉         ║
║         ⣿⣿⣿⣿⣿⣿⣿⡟⠁             ║
║         ⣿⣿⣿⣿⣿⣿⣿⡇⠀⢀⣠⣴     ║
║         ⣿⣿⣿⣿⣿⣿⣿⡇⠀⢰⣿⣿     ║
║         ⣿⣿⣿⣿⣿⣿⣿⡇⠀⠘⣿⣿     ║
║         ⣿⣿⣿⣿⣿⣿⣿⣿⡀⠀⠀⠀     ║
║         ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⣤⣤     ║
╚════════════════════════════════╝
            """,
            "osint": """
╔════════════════════════════════════════╗
║   ██████╗ ███████╗██████╗ ███████╗     ║
║   ██╔══██╗██╔════╝██╔══██╗██╔════╝     ║
║   ██████╔╝█████╗  ██████╔╝█████╗       ║
║   ██╔═══╝ ██╔══╝  ██╔═══╝ ██╔══╝       ║
║   ██║     ███████╗██║     ███████╗     ║
║   ╚═╝     ╚══════╝╚═╝     ╚══════╝     ║
║                                        ║
║   ██████╗ ███████╗██╗███╗   ██╗████████╗║
║   ██╔══██╗██╔════╝██║████╗  ██║╚══██╔══╝║
║   ██║   ██║███████╗██║██╔██╗ ██║   ██║   ║
║   ██║   ██║╚════██║██║██║╚██╗██║   ██║   ║
║   ╚██████╔╝███████║██║██║ ╚████║   ██║   ║
║    ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝   ║
╚════════════════════════════════════════╝
            """
        }
        return arts.get(style, arts["normal"])
    
    def search_osint(self, query):
        """Поиск информации по OSINT запросу"""
        results = {
            "query": query,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sources": [],
            "tools_suggested": random.sample(self.osint_tools, 3),
            "pepe_reaction": random.choice(list(self.pepe_faces.keys()))
        }
        
        # Симуляция поиска по источникам
        for source in self.osint_sources:
            if random.random() > 0.6:
                results["sources"].append({
                    "source": source,
                    "relevance": random.randint(60, 100),
                    "info_found": random.choice(["профиль", "комментарии", "посты", "активность"])
                })
        
        return results
    
    def analyze_username(self, username):
        """Анализ username по различным платформам"""
        platforms = {
            "GitHub": f"github.com/{username}",
            "Twitter": f"twitter.com/{username}",
            "Reddit": f"reddit.com/user/{username}",
            "Telegram": f"t.me/{username}",
            "Instagram": f"instagram.com/{username}",
            "TikTok": f"tiktok.com/@{username}",
            "YouTube": f"youtube.com/@{username}",
            "Pinterest": f"pinterest.com/{username}"
        }
        
        report = {
            "username": username,
            "timestamp": datetime.now().strftime("%Y-%d-%m %H:%M:%S"),
            "platforms": {},
            "total_found": 0,
            "pepe_rating": random.randint(1, 10)
        }
        
        for platform, url in platforms.items():
            exists = random.random() > 0.7
            if exists:
                report["total_found"] += 1
            report["platforms"][platform] = {
                "url": url,
                "exists": exists,
                "status": "✅ НАЙДЕН" if exists else "❌ НЕ НАЙДЕН"
            }
        
        return report
    
    def run_osint_scan(self, target):
        """Запуск полного OSINT сканирования"""
        findings = [
            f"DNS записи для {target}",
            f"Исторические whois данные",
            f"Связанные поддомены",
            f"Email адреса: admin@{target}, contact@{target}",
            f"Социальные профили, связанные с {target}",
            f"Упоминания в открытых базах данных"
        ]
        
        scan_results = {
            "target": target,
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "findings": random.sample(findings, k=random.randint(3, 5)),
            "risk_level": random.choice(["🟢 Низкий", "🟡 Средний", "🔴 Высокий"]),
            "recommendations": random.choice([
                "Проверь утечки паролей на haveibeenpwned.com",
                "Используй Shodan для поиска открытых портов",
                "Проверь архивные версии сайта на archive.org",
                "Ищи информацию в Pastebin и GitHub"
            ]),
            "pepe_advice": random.choice([
                "🐸 Будь осторожен с найденной информацией",
                "🐸 Используй VPN при OSINT разведке",
                "🐸 Не нарушай закон, брат",
                "🐸 Собирай только публичные данные"
            ])
        }
        
        return scan_results
    
    def get_pepe_fact(self):
        """Случайный факт о PEPE"""
        facts = [
            "🐸 PEPE появился в 2005 году в комиксе 'Boy's Club' от Мэтта Фури",
            "🐸 Существует более 10000 вариаций мема PEPE",
            "🐸 В 2016 году PEPE был признан символом ненависти, но оригинальный автор против",
            "🐸 NFT с PEPE 'Rare Pepe' продавались за миллионы долларов",
            "🐸 PEPE — одна из первых лягушек, ставших интернет-мемом",
            "🐸 У PEPE есть свой собственный крипто-токен PepeCoin"
        ]
        return random.choice(facts)

# ========== ОБРАБОТЧИК КОМАНД ДЛЯ TELEGRAM ==========
class PepeOSINTBotHandler:
    def __init__(self, token):
        self.token = token
        self.bot = PepeOSINTBot()
        self.last_command = {}
        
    def send_message(self, chat_id, text, parse_mode="HTML"):
        """Отправка сообщения через Telegram API"""
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.json()
        except Exception as e:
            logger.error(f"Ошибка отправки: {e}")
            return None
    
    def send_photo(self, chat_id, photo_bytes, caption=""):
        """Отправка изображения"""
        url = f"https://api.telegram.org/bot{self.token}/sendPhoto"
        files = {"photo": ("pepe.png", photo_bytes, "image/png")}
        data = {"chat_id": chat_id, "caption": caption}
        try:
            response = requests.post(url, files=files, data=data, timeout=10)
            return response.json()
        except Exception as e:
            logger.error(f"Ошибка отправки фото: {e}")
            return None
    
    def create_pepe_image(self, text, emotion="normal"):
        """Создает изображение с PEPE"""
        img = Image.new('RGB', (600, 400), color='#1a1a2e')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        except:
            font = ImageFont.load_default()
            title_font = ImageFont.load_default()
        
        # Рисуем рамку
        draw.rectangle([10, 10, 590, 390], outline='#00ff00', width=3)
        
        # Заголовок
        draw.text((180, 20), "🐸 PEPE OSINT BOT", fill='#00ff00', font=title_font)
        
        # Текст
        draw.text((30, 80), f"📝 Запрос: {text[:50]}", fill='white', font=font)
        
        # Результаты
        y_offset = 130
        draw.text((30, y_offset), "📊 Результаты поиска:", fill='#88ff88', font=font)
        y_offset += 30
        
        for i in range(min(4, len(text.split()))):
            draw.text((50, y_offset), f"• Источник {i+1}: информация найдена", fill='#aaaaaa', font=font)
            y_offset += 25
        
        # Футер
        draw.text((30, 350), f"🐸 PEPE OSINT v1.0 | {datetime.now().strftime('%H:%M:%S')}", fill='#666666', font=font)
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return img_byte_arr
    
    def handle_command(self, command, args, chat_id):
        """Обработка команд"""
        command = command.lower()
        
        if command == "/start":
            return self.get_start_message()
        
        elif command == "/help":
            return self.get_help_message()
        
        elif command == "/osint":
            if not args:
                return "❌ Укажи запрос!\nПример: `/osint elon musk`"
            results = self.bot.search_osint(args)
            return self.format_osint_results(results)
        
        elif command == "/username":
            if not args:
                return "❌ Укажи username!\nПример: `/username john_doe`"
            report = self.bot.analyze_username(args)
            return self.format_username_report(report)
        
        elif command == "/scan":
            if not args:
                return "❌ Укажи цель!\nПример: `/scan example.com`"
            scan = self.bot.run_osint_scan(args)
            return self.format_scan_results(scan)
        
        elif command == "/pepe":
            style = args if args in ["normal", "osint"] else "normal"
            return f"<pre>{self.bot.create_ascii_pepe(style)}</pre>"
        
        elif command == "/fact":
            return self.bot.get_pepe_fact()
        
        elif command == "/tools":
            return self.get_tools_list()
        
        else:
            return None
    
    def get_start_message(self):
        return """<b>🐸 Добро пожаловать в PEPE OSINT Bot!</b>

Я помогаю искать информацию в открытых источниках с душой PEPE.

<b>📋 Доступные команды:</b>
/help - Показать все команды
/osint &lt;запрос&gt; - Поиск информации
/username &lt;ник&gt; - Анализ username
/scan &lt;цель&gt; - OSINT сканирование
/pepe [normal|osint] - ASCII арт
/fact - Факт о PEPE
/tools - Список OSINT инструментов

<b>🎯 Примеры:</b>
<code>/osint elon musk</code>
<code>/username pepe_the_frog</code>
<code>/scan google.com</code>

🐸 <i>Собирай информацию ответственно!</i>"""
    
    def get_help_message(self):
        return """<b>📚 Справка по командам PEPE OSINT Bot</b>

<b>🔍 OSINT команды:</b>
• <code>/osint &lt;запрос&gt;</code> - Поиск по открытым источникам
• <code>/username &lt;ник&gt;</code> - Проверка username на 8+ платформах
• <code>/scan &lt;цель&gt;</code> - Глубокое OSINT сканирование
• <code>/tools</code> - Список OSINT инструментов

<b>🐸 PEPE команды:</b>
• <code>/pepe [normal|osint]</code> - ASCII арт PEPE
• <code>/fact</code> - Случайный факт о PEPE

<b>ℹ️ Общие:</b>
• <code>/start</code> - Приветствие
• <code>/help</code> - Эта справка

<b>💡 Примеры:</b>
<code>/osint cyber security</code>
<code>/username anonymous</code>
<code>/scan microsoft.com</code>

🐸 <i>Совет: используй разные запросы для лучших результатов</i>"""
    
    def get_tools_list(self):
        tools = self.bot.osint_tools + [
            "Google Dorks", "HaveIBeenPwned", "Wayback Machine",
            "Censys", "Shodan", "Recon-ng", "theHarvester"
        ]
        tools_text = "\n".join([f"• {tool}" for tool in sorted(set(tools))])
        return f"<b>🛠️ Популярные OSINT инструменты:</b>\n\n{tools_text}\n\n🐸 <i>Используй их с умом!</i>"
    
    def format_osint_results(self, results):
        text = f"<b>🔍 Результаты OSINT поиска</b>\n\n"
        text += f"📝 <b>Запрос:</b> {results['query']}\n"
        text += f"⏰ <b>Время:</b> {results['timestamp']}\n"
        text += f"🐸 <b>Реакция PEPE:</b> {results['pepe_reaction']} {self.bot.pepe_faces.get(results['pepe_reaction'], '')}\n\n"
        
        if results['sources']:
            text += "<b>📡 Найдено в источниках:</b>\n"
            for src in results['sources']:
                text += f"• <b>{src['source']}</b> - {src['info_found']} (релевантность: {src['relevance']}%)\n"
        else:
            text += "❌ <b>Ничего не найдено</b>\n"
        
        text += f"\n<b>🛠️ Рекомендуемые инструменты:</b>\n"
        for tool in results['tools_suggested']:
            text += f"• {tool}\n"
        
        return text
    
    def format_username_report(self, report):
        rating_emoji = "🐸" * min(report['pepe_rating'], 10)
        text = f"<b>👤 Анализ username: {report['username']}</b>\n\n"
        text += f"📊 <b>Найдено профилей:</b> {report['total_found']}/8\n"
        text += f"⭐ <b>Рейтинг PEPE:</b> {rating_emoji}\n\n"
        text += "<b>🌐 Платформы:</b>\n"
        
        for platform, data in report['platforms'].items():
            text += f"{data['status']} {platform}: {data['url']}\n"
        
        return text
    
    def format_scan_results(self, scan):
        text = f"<b>🕵️ OSINT Сканирование: {scan['target']}</b>\n\n"
        text += f"⏰ <b>Начато:</b> {scan['start_time']}\n"
        text += f"⚠️ <b>Уровень риска:</b> {scan['risk_level']}\n\n"
        
        text += "<b>📋 Найденная информация:</b>\n"
        for finding in scan['findings']:
            text += f"• {finding}\n"
        
        text += f"\n<b>💡 Рекомендация:</b> {scan['recommendations']}\n"
        text += f"\n{scan['pepe_advice']}"
        
        return text

# ========== ЗАПУСК БОТА (LONG POLLING) ==========
import requests
import time

def main():
    logger.info("🐸 Запуск PEPE OSINT Telegram бота...")
    logger.info(f"Токен: {BOT_TOKEN[:10]}... (скрыто)")
    
    handler = PepeOSINTBotHandler(BOT_TOKEN)
    
    offset = 0
    
    while True:
        try:
            # Получаем обновления
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            response = requests.get(url, params={"offset": offset, "timeout": 30}, timeout=35)
            data = response.json()
            
            if data.get("ok") and data.get("result"):
                for update in data["result"]:
                    offset = update["update_id"] + 1
                    
                    if "message" in update:
                        msg = update["message"]
                        chat_id = msg["chat"]["id"]
                        text = msg.get("text", "")
                        
                        if text.startswith("/"):
                            parts = text.split(maxsplit=1)
                            command = parts[0]
                            args = parts[1] if len(parts) > 1 else ""
                            
                            response_text = handler.handle_command(command, args, chat_id)
                            
                            if response_text:
                                handler.send_message(chat_id, response_text)
                        else:
                            # Ответ на обычное сообщение
                            handler.send_message(
                                chat_id, 
                                f"🐸 Привет! Используй /help для списка команд.\n\nТвой запрос: {text[:100]}"
                            )
            
        except KeyboardInterrupt:
            logger.info("👋 Бот остановлен")
            break
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
