import traceback
import time
import requests
import json
import re
import os
import shutil
from datetime import datetime, date, timedelta
from urllib.parse import quote_plus
from pathlib import Path
import sqlite3
import telebot
from telebot import types
import threading
import random
import itertools
import logging
import string
from functools import lru_cache
from threading import Lock

# ======================
# 🔧 إعدادات عامة
# ======================
USERNAME = "Medo123"
PASSWORD = "Bn_1411"
BOT_TOKEN = "8904582200:AAFmcpsnegZ1VBZ1a9xZ4VFIAOz-bQZ5278"
CHAT_IDS = [""]

REFRESH_INTERVAL = 3
TIMEOUT = 100
MAX_RETRIES = 5
RETRY_DELAY = 5

IDX_DATE = 0
IDX_NUMBER = 2
IDX_SMS = 5
SENT_MESSAGES_FILE = "sent_messages.json"

ADMIN_IDS = [6650935110]
DB_PATH = "bot.db"
USERS_BACKUP_FILE = "users_backup.json"
USERS_FILE = "users_ids.txt"
FORCE_SUB_CHANNEL = None
FORCE_SUB_ENABLED = False
BOT_ACTIVE = True

DEFAULT_POINTS_TO_UNLOCK = 5
REFERRAL_POINTS = 1
INVITE_BONUS = 3

db_lock = Lock()

# ======================
# 🌍 رموز الدول
# ======================
COUNTRY_CODES = {
    "1": ("USA/Canada", "🇺🇸", "US"),
    "7": ("Russia", "🇷🇺", "RU"),
    "20": ("Egypt", "🇪🇬", "EG"),
    "27": ("South Africa", "🇿🇦", "ZA"),
    "30": ("Greece", "🇬🇷", "GR"),
    "31": ("Netherlands", "🇳🇱", "NL"),
    "32": ("Belgium", "🇧🇪", "BE"),
    "33": ("France", "🇫🇷", "FR"),
    "34": ("Spain", "🇪🇸", "ES"),
    "36": ("Hungary", "🇭🇺", "HU"),
    "39": ("Italy", "🇮🇹", "IT"),
    "40": ("Romania", "🇷🇴", "RO"),
    "41": ("Switzerland", "🇨🇭", "CH"),
    "42": ("????", "❓", "??"),
    "43": ("Austria", "🇦🇹", "AT"),
    "44": ("United Kingdom", "🇬🇧", "UK"),
    "45": ("Denmark", "🇩🇰", "DK"),
    "46": ("Sweden", "🇸🇪", "SE"),
    "47": ("Norway", "🇳🇴", "NO"),
    "48": ("Poland", "🇵🇱", "PL"),
    "49": ("Germany", "🇩🇪", "DE"),
    "51": ("Peru", "🇵🇪", "PE"),
    "52": ("Mexico", "🇲🇽", "MX"),
    "53": ("Cuba", "🇨🇺", "CU"),
    "54": ("Argentina", "🇦🇷", "AR"),
    "55": ("Brazil", "🇧🇷", "BR"),
    "56": ("Chile", "🇨🇱", "CL"),
    "57": ("Colombia", "🇨🇴", "CO"),
    "58": ("Venezuela", "🇻🇪", "VE"),
    "60": ("Malaysia", "🇲🇾", "MY"),
    "61": ("Australia", "🇦🇺", "AU"),
    "62": ("Indonesia", "🇮🇩", "ID"),
    "63": ("Philippines", "🇵🇭", "PH"),
    "64": ("New Zealand", "🇳🇿", "NZ"),
    "65": ("Singapore", "🇸🇬", "SG"),
    "66": ("Thailand", "🇹🇭", "TH"),
    "81": ("Japan", "🇯🇵", "JP"),
    "82": ("South Korea", "🇰🇷", "KR"),
    "84": ("Vietnam", "🇻🇳", "VN"),
    "86": ("China", "🇨🇳", "CN"),
    "90": ("Turkey", "🇹🇷", "TR"),
    "91": ("India", "🇮🇳", "IN"),
    "92": ("Pakistan", "🇵🇰", "PK"),
    "93": ("Afghanistan", "🇦🇫", "AF"),
    "94": ("Sri Lanka", "🇱🇰", "LK"),
    "95": ("Myanmar", "🇲🇲", "MM"),
    "98": ("Iran", "🇮🇷", "IR"),
    "211": ("South Sudan", "🇸🇸", "SS"),
    "212": ("Morocco", "🇲🇦", "MA"),
    "213": ("Algeria", "🇩🇿", "DZ"),
    "216": ("Tunisia", "🇹🇳", "TN"),
    "218": ("Libya", "🇱🇾", "LY"),
    "220": ("Gambia", "🇬🇲", "GM"),
    "221": ("Senegal", "🇸🇳", "SN"),
    "222": ("Mauritania", "🇲🇷", "MR"),
    "223": ("Mali", "🇲🇱", "ML"),
    "224": ("Guinea", "🇬🇳", "GN"),
    "225": ("Ivory Coast", "🇨🇮", "CI"),
    "226": ("Burkina Faso", "🇧🇫", "BF"),
    "227": ("Niger", "🇳🇪", "NE"),
    "228": ("Togo", "🇹🇬", "TG"),
    "229": ("Benin", "🇧🇯", "BJ"),
    "230": ("Mauritius", "🇲🇺", "MU"),
    "231": ("Liberia", "🇱🇷", "LR"),
    "232": ("Sierra Leone", "🇸🇱", "SL"),
    "233": ("Ghana", "🇬🇭", "GH"),
    "234": ("Nigeria", "🇳🇬", "NG"),
    "235": ("Chad", "🇹🇩", "TD"),
    "236": ("Central African Rep", "🇨🇫", "CF"),
    "237": ("Cameroon", "🇨🇲", "CM"),
    "238": ("Cape Verde", "🇨🇻", "CV"),
    "239": ("Sao Tome", "🇸🇹", "ST"),
    "240": ("Equatorial Guinea", "🇬🇶", "GQ"),
    "241": ("Gabon", "🇬🇦", "GA"),
    "242": ("Congo", "🇨🇬", "CG"),
    "243": ("DR Congo", "🇨🇩", "CD"),
    "244": ("Angola", "🇦🇴", "AO"),
    "245": ("Guinea-Bissau", "🇬🇼", "GW"),
    "248": ("Seychelles", "🇸🇨", "SC"),
    "249": ("Sudan", "🇸🇩", "SD"),
    "250": ("Rwanda", "🇷🇼", "RW"),
    "251": ("Ethiopia", "🇪🇹", "ET"),
    "252": ("Somalia", "🇸🇴", "SO"),
    "253": ("Djibouti", "🇩🇯", "DJ"),
    "254": ("Kenya", "🇰🇪", "KE"),
    "255": ("Tanzania", "🇹🇿", "TZ"),
    "256": ("Uganda", "🇺🇬", "UG"),
    "257": ("Burundi", "🇧🇮", "BI"),
    "258": ("Mozambique", "🇲🇿", "MZ"),
    "260": ("Zambia", "🇿🇲", "ZM"),
    "261": ("Madagascar", "🇲🇬", "MG"),
    "262": ("Reunion", "🇷🇪", "RE"),
    "263": ("Zimbabwe", "🇿🇼", "ZW"),
    "264": ("Namibia", "🇳🇦", "NA"),
    "265": ("Malawi", "🇲🇼", "MW"),
    "266": ("Lesotho", "🇱🇸", "LS"),
    "267": ("Botswana", "🇧🇼", "BW"),
    "268": ("Eswatini", "🇸🇿", "SZ"),
    "269": ("Comoros", "🇰🇲", "KM"),
    "350": ("Gibraltar", "🇬🇮", "GI"),
    "351": ("Portugal", "🇵🇹", "PT"),
    "352": ("Luxembourg", "🇱🇺", "LU"),
    "353": ("Ireland", "🇮🇪", "IE"),
    "354": ("Iceland", "🇮🇸", "IS"),
    "355": ("Albania", "🇦🇱", "AL"),
    "356": ("Malta", "🇲🇹", "MT"),
    "357": ("Cyprus", "🇨🇾", "CY"),
    "358": ("Finland", "🇫🇮", "FI"),
    "359": ("Bulgaria", "🇧🇬", "BG"),
    "370": ("Lithuania", "🇱🇹", "LT"),
    "371": ("Latvia", "🇱🇻", "LV"),
    "372": ("Estonia", "🇪🇪", "EE"),
    "373": ("Moldova", "🇲🇩", "MD"),
    "374": ("Armenia", "🇦🇲", "AM"),
    "375": ("Belarus", "🇧🇾", "BY"),
    "376": ("Andorra", "🇦🇩", "AD"),
    "377": ("Monaco", "🇲🇨", "MC"),
    "378": ("San Marino", "🇸🇲", "SM"),
    "380": ("Ukraine", "🇺🇦", "UA"),
    "381": ("Serbia", "🇷🇸", "RS"),
    "382": ("Montenegro", "🇲🇪", "ME"),
    "383": ("Kosovo", "🇽🇰", "XK"),
    "385": ("Croatia", "🇭🇷", "HR"),
    "386": ("Slovenia", "🇸🇮", "SI"),
    "387": ("Bosnia", "🇧🇦", "BA"),
    "389": ("North Macedonia", "🇲🇰", "MK"),
    "420": ("Czech Republic", "🇨🇿", "CZ"),
    "421": ("Slovakia", "🇸🇰", "SK"),
    "423": ("Liechtenstein", "🇱🇮", "LI"),
    "500": ("Falkland Islands", "🇫🇰", "FK"),
    "501": ("Belize", "🇧🇿", "BZ"),
    "502": ("Guatemala", "🇬🇹", "GT"),
    "503": ("El Salvador", "🇸🇻", "SV"),
    "504": ("Honduras", "🇭🇳", "HN"),
    "505": ("Nicaragua", "🇳🇮", "NI"),
    "506": ("Costa Rica", "🇨🇷", "CR"),
    "507": ("Panama", "🇵🇦", "PA"),
    "509": ("Haiti", "🇭🇹", "HT"),
    "591": ("Bolivia", "🇧🇴", "BO"),
    "592": ("Guyana", "🇬🇾", "GY"),
    "593": ("Ecuador", "🇪🇨", "EC"),
    "595": ("Paraguay", "🇵🇾", "PY"),
    "597": ("Suriname", "🇸🇷", "SR"),
    "598": ("Uruguay", "🇺🇾", "UY"),
    "670": ("Timor-Leste", "🇹🇱", "TL"),
    "673": ("Brunei", "🇧🇳", "BN"),
    "674": ("Nauru", "🇳🇷", "NR"),
    "675": ("Papua New Guinea", "🇵🇬", "PG"),
    "676": ("Tonga", "🇹🇴", "TO"),
    "677": ("Solomon Islands", "🇸🇧", "SB"),
    "678": ("Vanuatu", "🇻🇺", "VU"),
    "679": ("Fiji", "🇫🇯", "FJ"),
    "680": ("Palau", "🇵🇼", "PW"),
    "685": ("Samoa", "🇼🇸", "WS"),
    "686": ("Kiribati", "🇰🇮", "KI"),
    "687": ("New Caledonia", "🇳🇨", "NC"),
    "688": ("Tuvalu", "🇹🇻", "TV"),
    "689": ("French Polynesia", "🇵🇫", "PF"),
    "691": ("Micronesia", "🇫🇲", "FM"),
    "692": ("Marshall Islands", "🇲🇭", "MH"),
    "850": ("North Korea", "🇰🇵", "KP"),
    "852": ("Hong Kong", "🇭🇰", "HK"),
    "853": ("Macau", "🇲🇴", "MO"),
    "855": ("Cambodia", "🇰🇭", "KH"),
    "856": ("Laos", "🇱🇦", "LA"),
    "960": ("Maldives", "🇲🇻", "MV"),
    "961": ("Lebanon", "🇱🇧", "LB"),
    "962": ("Jordan", "🇯🇴", "JO"),
    "963": ("Syria", "🇸🇾", "SY"),
    "964": ("Iraq", "🇮🇶", "IQ"),
    "965": ("Kuwait", "🇰🇼", "KW"),
    "966": ("Saudi Arabia", "🇸🇦", "SA"),
    "967": ("Yemen", "🇾🇪", "YE"),
    "968": ("Oman", "🇴🇲", "OM"),
    "970": ("Palestine", "🇵🇸", "PS"),
    "971": ("UAE", "🇦🇪", "AE"),
    "972": ("Israel", "🇮🇱", "IL"),
    "973": ("Bahrain", "🇧🇭", "BH"),
    "974": ("Qatar", "🇶🇦", "QA"),
    "975": ("Bhutan", "🇧🇹", "BT"),
    "976": ("Mongolia", "🇲🇳", "MN"),
    "977": ("Nepal", "🇳🇵", "NP"),
    "992": ("Tajikistan", "🇹🇯", "TJ"),
    "993": ("Turkmenistan", "🇹🇲", "TM"),
    "994": ("Azerbaijan", "🇦🇿", "AZ"),
    "995": ("Georgia", "🇬🇪", "GE"),
    "996": ("Kyrgyzstan", "🇰🇬", "KG"),
    "998": ("Uzbekistan", "🇺🇿", "UZ"),
}

# ======================
# 📁 نظام النسخ الاحتياطي للمستخدمين
# ======================

def backup_users_to_file():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT user_id, username, first_name, last_name, points, total_invites, referred_by, join_date, is_banned FROM users")
        users = c.fetchall()
        conn.close()

        users_data = []
        for user in users:
            users_data.append({
                'user_id': user[0],
                'username': user[1],
                'first_name': user[2],
                'last_name': user[3],
                'points': user[4],
                'total_invites': user[5] or 0,
                'referred_by': user[6],
                'join_date': user[7],
                'is_banned': user[8] or 0
            })

        with open(USERS_BACKUP_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, ensure_ascii=False, indent=2)

        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            for user in users_data:
                f.write(f"{user['user_id']}\n")

        print(f"✅ تم نسخ {len(users_data)} مستخدم إلى {USERS_BACKUP_FILE}")
        return True
    except Exception as e:
        print(f"❌ خطأ في النسخ الاحتياطي: {e}")
        return False

def restore_users_from_backup():
    try:
        if not os.path.exists(USERS_BACKUP_FILE):
            print("⚠️ لا يوجد ملف نسخ احتياطي للمستخدمين")
            return False

        with open(USERS_BACKUP_FILE, 'r', encoding='utf-8') as f:
            users_data = json.load(f)

        if not users_data:
            return False

        conn = get_db_connection()
        c = conn.cursor()

        for user in users_data:
            c.execute("""
                INSERT OR REPLACE INTO users
                (user_id, username, first_name, last_name, points, total_invites, referred_by, join_date, is_banned)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (
                user['user_id'], user['username'], user['first_name'], user['last_name'],
                user['points'], user['total_invites'], user['referred_by'],
                user['join_date'], user['is_banned']
            ))

        conn.commit()
        conn.close()

        print(f"✅ تم استعادة {len(users_data)} مستخدم من النسخ الاحتياطي")
        return True
    except Exception as e:
        print(f"❌ خطأ في الاستعادة: {e}")
        return False

def check_and_restore_db():
    if not os.path.exists(DB_PATH):
        print("⚠️ قاعدة البيانات غير موجودة، جاري إنشاء جديدة واستعادة المستخدمين...")
        init_db()
        restore_users_from_backup()
        return True
    return False

# ======================
# 🧰 دوال إدارة قاعدة البيانات
# ======================

def get_db_connection():
    return sqlite3.connect(DB_PATH, timeout=30.0, check_same_thread=False)

def get_setting(key):
    with db_lock:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT value FROM bot_settings WHERE key=?", (key,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else None

def set_setting(key, value):
    with db_lock:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("REPLACE INTO bot_settings (key, value) VALUES (?,?)", (key, value))
        conn.commit()
        conn.close()

def init_db():
    with db_lock:
        conn = get_db_connection()
        c = conn.cursor()

        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                country_code TEXT,
                assigned_number TEXT,
                is_banned INTEGER DEFAULT 0,
                private_combo_country TEXT DEFAULT NULL,
                points INTEGER DEFAULT 0,
                referred_by INTEGER DEFAULT NULL,
                total_invites INTEGER DEFAULT 0,
                join_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS files_lists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                description TEXT DEFAULT '',
                points_required INTEGER DEFAULT 5,
                numbers TEXT,
                created_by INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS user_purchases (
                user_id INTEGER,
                file_id INTEGER,
                purchase_date TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, file_id)
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS referrals_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER,
                referred_id INTEGER,
                points_awarded INTEGER DEFAULT 1,
                referral_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS combos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                country_code TEXT,
                combo_index INTEGER DEFAULT 1,
                numbers TEXT,
                UNIQUE(country_code, combo_index)
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS otp_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number TEXT,
                otp TEXT,
                full_message TEXT,
                timestamp TEXT,
                assigned_to INTEGER
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS bot_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS private_combos (
                user_id INTEGER,
                country_code TEXT,
                numbers TEXT,
                PRIMARY KEY (user_id, country_code)
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS force_sub_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_url TEXT UNIQUE NOT NULL,
                description TEXT DEFAULT '',
                enabled INTEGER DEFAULT 1
            )
        ''')

        c.execute("CREATE INDEX IF NOT EXISTS idx_users_points ON users(points)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_users_assigned ON users(assigned_number)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_purchases_user ON user_purchases(user_id)")

        c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('force_sub_channel', '')")
        c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('force_sub_enabled', '0')")
        c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('default_points', '5')")

        conn.commit()
        conn.close()

    if os.path.exists(USERS_BACKUP_FILE):
        restore_users_from_backup()

init_db()

# ======================
# 🔒 دوال الاشتراك الاجباري - جديد
# ======================
def get_force_sub_channels():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT channel_url FROM force_sub_channels WHERE enabled=1")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

def get_all_force_sub_channels_admin():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, channel_url, enabled FROM force_sub_channels ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def add_force_sub_channel(channel_url):
    with db_lock:
        conn = get_db_connection()
        c = conn.cursor()
        try:
            c.execute("INSERT INTO force_sub_channels (channel_url) VALUES (?)", (channel_url.strip(),))
            conn.commit()
            conn.close()
            return True
        except:
            conn.close()
            return False

def delete_force_sub_channel(channel_id):
    with db_lock:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM force_sub_channels WHERE id=?", (channel_id,))
        conn.commit()
        conn.close()

def is_force_sub_enabled():
    val = get_setting('force_sub_enabled')
    return val == '1'

def toggle_force_sub():
    current = is_force_sub_enabled()
    set_setting('force_sub_enabled', '0' if current else '1')
    return not current

def parse_channel_username(channel_url):
    url = channel_url.strip()
    url = url.replace("https://t.me/", "").replace("http://t.me/", "").replace("t.me/", "").replace("@", "").split("/")[0]
    return url

def check_user_is_subscribed(user_id):
    if not is_force_sub_enabled():
        return True
    channels = get_force_sub_channels()
    if not channels:
        return True
    for channel_url in channels:
        try:
            username = parse_channel_username(channel_url)
            # نحاول نجيب الـ chat_id
            chat = bot.get_chat(f"@{username}")
            member = bot.get_chat_member(chat.id, user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception as e:
            # اذا البوت مو ادمن بالقناة ما يكدر يفحص، نعتبره مشترك حتى لا يعلق البوت
            # لكن الافضل تخلي البوت ادمن بالقناة
            print(f"Force sub check error for {channel_url}: {e}")
            # لو ما كدرنا نتاكد، نرجع False حتى يجبره يشترك
            try:
                # محاولة ثانية مباشرة باليوزر
                member = bot.get_chat_member(f"@{username}", user_id)
                if member.status in ['left', 'kicked']:
                    return False
            except:
                return False
    return True

def get_force_sub_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    channels = get_force_sub_channels()
    for ch in channels:
        username = parse_channel_username(ch)
        markup.add(types.InlineKeyboardButton(f"📢 اشترك في @{username}", url=f"https://t.me/{username}", style='primary'))
    markup.add(types.InlineKeyboardButton("✅ تحققت من الاشتراك", callback_data="check_force_sub", style='success'))
    return markup

# ======================
# 🎯 دوال النظام الأساسية
# ======================

@lru_cache(maxsize=1000)
def get_user_points_cached(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT points FROM users WHERE user_id =?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

def get_user_points(user_id):
    return get_user_points_cached(user_id)

def invalidate_user_cache(user_id):
    get_user_points_cached.cache_clear()

def add_points(user_id, points, reason=""):
    with db_lock:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE users SET points = points +? WHERE user_id =?", (points, user_id))
        conn.commit()
        conn.close()
    invalidate_user_cache(user_id)
    backup_users_to_file()
    print(f"[+] تم إضافة {points} نقطة للمستخدم {user_id}")
    return True

def deduct_points(user_id, points):
    current = get_user_points(user_id)
    if current < points:
        return False
    with db_lock:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE users SET points = points -? WHERE user_id =?", (points, user_id))
        conn.commit()
        conn.close()
    invalidate_user_cache(user_id)
    backup_users_to_file()
    return True

def get_user(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id =?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def save_user(user_id, username="", first_name="", last_name="", country_code=None, assigned_number=None, private_combo_country=None, referred_by=None):
    with db_lock:
        conn = get_db_connection()
        c = conn.cursor()
        existing_data = get_user(user_id)

        if existing_data:
            if country_code is None:
                country_code = existing_data[4] if len(existing_data) > 4 else None
            if assigned_number is None:
                assigned_number = existing_data[5] if len(existing_data) > 5 else None
            if private_combo_country is None:
                private_combo_country = existing_data[7] if len(existing_data) > 7 else None
            points = existing_data[8] if len(existing_data) > 8 else 0
            total_invites = existing_data[10] if len(existing_data) > 10 else 0
            referred_by = existing_data[9] if len(existing_data) > 9 else referred_by
        else:
            points = 0
            total_invites = 0
            save_user_id_to_file(user_id)

        c.execute("""
            REPLACE INTO users (user_id, username, first_name, last_name, country_code, assigned_number, is_banned, private_combo_country, points, referred_by, total_invites)
            VALUES (?,?,?,?,?,?, COALESCE((SELECT is_banned FROM users WHERE user_id=?), 0),?,?,?,?)
        """, (
            user_id, username, first_name, last_name, country_code, assigned_number,
            user_id, private_combo_country, points, referred_by, total_invites
        ))
        conn.commit()
        conn.close()

    invalidate_user_cache(user_id)
    backup_users_to_file()

def ban_user(user_id):
    with db_lock:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE users SET is_banned=1 WHERE user_id=?", (user_id,))
        conn.commit()
        conn.close()
    invalidate_user_cache(user_id)
    backup_users_to_file()

def unban_user(user_id):
    with db_lock:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE users SET is_banned=0 WHERE user_id=?", (user_id,))
        conn.commit()
        conn.close()
    invalidate_user_cache(user_id)
    backup_users_to_file()

def is_banned(user_id):
    user = get_user(user_id)
    return user and user[6] == 1

def is_maintenance_mode():
    return not BOT_ACTIVE

def set_maintenance_mode(status):
    global BOT_ACTIVE
    BOT_ACTIVE = not status

def save_user_id_to_file(user_id):
    try:
        existing_ids = set()
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and line.isdigit():
                        existing_ids.add(int(line))

        if user_id not in existing_ids:
            with open(USERS_FILE, 'a', encoding='utf-8') as f:
                f.write(f"{user_id}\n")
            return True
        return False
    except Exception as e:
        print(f"خطأ في حفظ الايدي: {e}")
        return False

def get_all_user_ids_from_file():
    try:
        if not os.path.exists(USERS_FILE):
            return []
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return [int(line.strip()) for line in f if line.strip().isdigit()]
    except Exception as e:
        print(f"خطأ في قراءة الايديات: {e}")
        return []

def get_all_users():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE is_banned=0")
    users = [row[0] for row in c.fetchall()]
    conn.close()

    for user_id in users:
        save_user_id_to_file(user_id)

    return users

# ======================
# 📁 دوال الكومبوهات
# ======================

def get_combo(country_code, combo_index=1, user_id=None):
    conn = get_db_connection()
    c = conn.cursor()
    if user_id:
        c.execute("SELECT numbers FROM private_combos WHERE user_id=? AND country_code=?", (user_id, country_code))
        row = c.fetchone()
        if row:
            conn.close()
            return json.loads(row[0])
    c.execute("SELECT numbers FROM combos WHERE country_code=? AND combo_index=?", (country_code, combo_index))
    row = c.fetchone()
    conn.close()
    return json.loads(row[0]) if row else []

def save_combo(country_code, numbers, user_id=None):
    with db_lock:
        conn = get_db_connection()
        c = conn.cursor()
        if user_id:
            c.execute("REPLACE INTO private_combos (user_id, country_code, numbers) VALUES (?,?,?)",
                      (user_id, country_code, json.dumps(numbers)))
        else:
            c.execute("SELECT MAX(combo_index) FROM combos WHERE country_code=?", (country_code,))
            max_index = c.fetchone()[0]
            next_index = 1 if max_index is None else max_index + 1
            c.execute("INSERT INTO combos (country_code, combo_index, numbers) VALUES (?,?,?)",
                      (country_code, next_index, json.dumps(numbers)))
        conn.commit()
        conn.close()

def delete_combo_number(country_code, number_to_delete, combo_index=1, user_id=None):
    numbers = get_combo(country_code, combo_index, user_id)
    if not numbers or number_to_delete not in numbers:
        return False

    numbers.remove(number_to_delete)

    with db_lock:
        conn = get_db_connection()
        c = conn.cursor()
        if user_id:
            c.execute("REPLACE INTO private_combos (user_id, country_code, numbers) VALUES (?,?,?)",
                      (user_id, country_code, json.dumps(numbers)))
        else:
            c.execute("UPDATE combos SET numbers =? WHERE country_code=? AND combo_index=?",
                      (json.dumps(numbers), country_code, combo_index))
        conn.commit()
        conn.close()
    return True

def get_all_combos():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT country_code, combo_index FROM combos ORDER BY country_code, combo_index")
    combos = c.fetchall()
    conn.close()
    return combos

def delete_combo(country_code, combo_index=None, user_id=None):
    with db_lock:
        conn = get_db_connection()
        c = conn.cursor()

        if user_id:
            c.execute("DELETE FROM private_combos WHERE user_id=? AND country_code=?", (user_id, country_code))
        elif combo_index:
            c.execute("DELETE FROM combos WHERE country_code=? AND combo_index=?", (country_code, combo_index))
        else:
            c.execute("DELETE FROM combos WHERE country_code=?", (country_code,))

        conn.commit()
        conn.close()
    return True

# ======================
# 📁 دوال الملفات
# ======================

def delete_file_list(file_id):
    try:
        with db_lock:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("UPDATE files_lists SET is_active = 0 WHERE id =?", (file_id,))
            conn.commit()
            conn.close()
        return True
    except Exception as e:
        print(f"❌ خطأ في حذف الملف: {e}")
        return False

def delete_file_permanently(file_id):
    try:
        with db_lock:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("DELETE FROM user_purchases WHERE file_id =?", (file_id,))
            c.execute("DELETE FROM files_lists WHERE id =?", (file_id,))
            conn.commit()
            conn.close()
        return True
    except Exception as e:
        print(f"❌ خطأ في الحذف النهائي: {e}")
        return False

def add_file_list(file_name, description, numbers, points_required, created_by):
    with db_lock:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''
            INSERT INTO files_lists (file_name, description, points_required, numbers, created_by)
            VALUES (?,?,?,?,?)
        ''', (file_name, description, points_required, json.dumps(numbers), created_by))
        file_id = c.lastrowid
        conn.commit()
        conn.close()
    return file_id

def get_all_files():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT id, file_name, description, points_required, created_by, created_at
        FROM files_lists
        WHERE is_active = 1
        ORDER BY created_at DESC
    ''')
    rows = c.fetchall()
    conn.close()
    return rows

def get_file_by_id(file_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT id, file_name, description, points_required, numbers, created_by, created_at FROM files_lists WHERE id =? AND is_active = 1', (file_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            'id': row[0],
            'file_name': row[1],
            'description': row[2],
            'points_required': row[3],
            'numbers': json.loads(row[4]),
            'created_by': row[5],
            'created_at': row[6]
        }
    return None

def has_user_purchased_file(user_id, file_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT 1 FROM user_purchases WHERE user_id =? AND file_id =?', (user_id, file_id))
    row = c.fetchone()
    conn.close()
    return row is not None

def purchase_file(user_id, file_id):
    if has_user_purchased_file(user_id, file_id):
        return False, "already_purchased"

    file_data = get_file_by_id(file_id)
    if not file_data:
        return False, "not_found"

    points_required = file_data['points_required']
    current_points = get_user_points(user_id)

    if current_points < points_required:
        return False, "insufficient_points"

    if not deduct_points(user_id, points_required):
        return False, "deduct_failed"

    with db_lock:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('INSERT INTO user_purchases (user_id, file_id) VALUES (?,?)', (user_id, file_id))
        conn.commit()
        conn.close()

    return True, "success"

def get_user_purchased_files(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT f.id, f.file_name, f.description, f.points_required, f.created_at, up.purchase_date
        FROM files_lists f
        JOIN user_purchases up ON f.id = up.file_id
        WHERE up.user_id =? AND f.is_active = 1
        ORDER BY up.purchase_date DESC
    ''', (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

# ======================
# 🎁 دوال الدعوات
# ======================

def process_referral(referrer_id, referred_id):
    if referrer_id == referred_id:
        return False, 0, 0

    with db_lock:
        conn = get_db_connection()
        c = conn.cursor()

        c.execute("SELECT 1 FROM referrals_log WHERE referrer_id =? AND referred_id =?",
                  (referrer_id, referred_id))
        if c.fetchone():
            conn.close()
            return False, 0, 0

        c.execute("SELECT total_invites FROM users WHERE user_id =?", (referrer_id,))
        current_invites_row = c.fetchone()

        if current_invites_row is None:
            current_count = 0
            c.execute("INSERT OR IGNORE INTO users (user_id, points, total_invites) VALUES (?,?,?)",
                      (referrer_id, 0, 0))
        else:
            current_count = current_invites_row[0] if current_invites_row[0] is not None else 0

        c.execute("INSERT INTO referrals_log (referrer_id, referred_id, points_awarded) VALUES (?,?,?)",
                  (referrer_id, referred_id, REFERRAL_POINTS))

        c.execute("UPDATE users SET points = points +?, total_invites = total_invites + 1 WHERE user_id =?",
                  (REFERRAL_POINTS, referrer_id))

        new_count = current_count + 1
        bonus_points = 0
        if new_count % 5 == 0:
            c.execute("UPDATE users SET points = points +? WHERE user_id =?", (INVITE_BONUS, referrer_id))
            bonus_points = INVITE_BONUS

        conn.commit()
        conn.close()

    invalidate_user_cache(referrer_id)
    backup_users_to_file()

    return True, REFERRAL_POINTS, bonus_points

def get_user_invites_count(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT total_invites FROM users WHERE user_id =?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

def get_invites_list(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT r.referred_id, u.username, u.first_name, r.referral_date
        FROM referrals_log r
        LEFT JOIN users u ON r.referred_id = u.user_id
        WHERE r.referrer_id =?
        ORDER BY r.referral_date DESC
    ''', (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

# ======================
# 🛠️ دوال مساعدة
# ======================

def clean_number(number):
    if not number:
        return ""
    number = re.sub(r'\D', '', str(number))
    return number

def get_country_info(number):
    number = number.strip().replace("+", "").replace(" ", "").replace("-", "")
    for code, (name, flag, short) in COUNTRY_CODES.items():
        if number.startswith(code):
            return name, flag, short
    return "Unknown", "🌍", "UN"

def mask_number(number):
    number = number.strip()
    if len(number) > 8:
        return number[:4] + "••••" + number[-3:]
    return number

def extract_otp(message):
    patterns = [
        r'(?:code|رمز|كود|verification|otp|pin)[:\s]+(\d{3,8})',
        r'\b(\d{4,8})\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group(1)
    return "N/A"

def detect_service(message):
    message_lower = message.lower()
    services = {
        "#WP": ["whatsapp", "واتساب"],
        "#FB": ["facebook", "فيسبوك"],
        "#TG": ["telegram", "تيليجرام"],
        "#IG": ["instagram", "انستقرام"],
    }
    for service_code, keywords in services.items():
        for keyword in keywords:
            if keyword in message_lower:
                return service_code
    return "Unknown"

def safe_html(text):
    if not text:
        return ""
    text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text

def is_admin(user_id):
    return user_id in ADMIN_IDS

def assign_number_to_user(user_id, number):
    with db_lock:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE users SET assigned_number=? WHERE user_id=?", (number, user_id))
        conn.commit()
        conn.close()

def get_user_by_number(number):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE assigned_number=?", (number,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def release_number(old_number):
    if not old_number:
        return
    with db_lock:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE users SET assigned_number=NULL WHERE assigned_number=?", (old_number,))
        conn.commit()
        conn.close()

def get_available_numbers(country_code, combo_index=1, user_id=None):
    all_numbers = get_combo(country_code, combo_index, user_id)
    if not all_numbers:
        return []
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT assigned_number FROM users WHERE assigned_number IS NOT NULL AND assigned_number!= ''")
    used_numbers = set(row[0] for row in c.fetchall())
    conn.close()
    available = [num for num in all_numbers if num not in used_numbers]
    return available

def log_otp(number, otp, full_message, assigned_to=None):
    with db_lock:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO otp_logs (number, otp, full_message, timestamp, assigned_to) VALUES (?,?,?,?,?)",
                  (number, otp, full_message, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), assigned_to))
        conn.commit()
        conn.close()

# ======================
# 🤖 البوت - الأوامر الرئيسية
# ======================

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    check_and_restore_db()

    args = message.text.split()
    referral_processed = False
    referral_points = 0
    referral_bonus = 0

    if len(args) > 1:
        try:
            referrer_id = int(args[1])
            if referrer_id and referrer_id!= user_id:
                if not get_user(user_id):
                    save_user(user_id, message.from_user.username or "",
                             message.from_user.first_name or "",
                             message.from_user.last_name or "",
                             referred_by=referrer_id)

                    success, points_awarded, bonus_awarded = process_referral(referrer_id, user_id)
                    if success:
                        referral_processed = True
                        referral_points = points_awarded
                        referral_bonus = bonus_awarded

                        welcome_referral = (
                            f"🎉 مرحباً بك!\n"
                            f"────────────────────\n"
                            f"لقد انضممت عبر دعوة من مستخدم آخر.\n"
                            f"تمت إضافة نقاط للمستخدم الذي دعاك.\n"
                            f"يمكنك البدء في استخدام البوت!"
                        )
                        try:
                            bot.send_message(user_id, welcome_referral, parse_mode="HTML")
                        except:
                            pass
                else:
                    try:
                        already_registered = f"ℹ️ أنت مسجل بالفعل في البوت!"
                        bot.send_message(user_id, already_registered, parse_mode="HTML")
                    except:
                        pass
        except ValueError:
            pass
        except Exception as e:
            print(f"خطأ في معالجة الدعوة: {e}")

    if is_maintenance_mode() and not is_admin(user_id):
        bot.send_message(chat_id, "⚠️ البوت في وضع الصيانة حالياً.", parse_mode="HTML")
        return

    if is_banned(user_id):
        bot.reply_to(message, "🚫 عذراً، لقد تم حظرك.", parse_mode="HTML")
        return

    # ===== فحص الاشتراك الاجباري =====
    if not is_admin(user_id) and is_force_sub_enabled():
        if not check_user_is_subscribed(user_id):
            bot.send_message(
                chat_id,
                "⚠️ <b>يجب عليك الاشتراك في القنوات اولاً لاستخدام البوت</b>\n\n"
                "اشترك ثم اضغط تحقق ✅",
                parse_mode="HTML",
                reply_markup=get_force_sub_markup()
            )
            return
    # ================================

    if not get_user(user_id):
        save_user(user_id, message.from_user.username or "",
                 message.from_user.first_name or "",
                 message.from_user.last_name or "")
        for admin in ADMIN_IDS:
            try:
                bot.send_message(admin, f"🆕 مستخدم جديد: `{user_id}`\n👤 @{message.from_user.username or 'لا يوجد'}", parse_mode="HTML")
            except:
                pass

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton("📞 أرقام مجانية", callback_data="show_numbers_menu", style='primary'),
        types.InlineKeyboardButton("قسم ارقام مدفوعه 🔥", callback_data="my_files_menu", style='success')
    )
    markup.row(
        types.InlineKeyboardButton("🏆 نقاطي", callback_data="show_points", style='primary'),
        types.InlineKeyboardButton("🎁 دعوة أصدقاء", callback_data="referral_menu", style='primary')
    )

    if is_admin(user_id):
        markup.row(types.InlineKeyboardButton("🔐 لوحة التحكم", callback_data="admin_panel", style='danger'))

    user_points = get_user_points(user_id)

    notification_text = ""
    if referral_processed:
        notification_text = f"🎉 تمت دعوتك بنجاح!\n"
        notification_text += f"⭐ المستخدم الذي دعاك حصل على +{referral_points} نقطة"
        if referral_bonus > 0:
            notification_text += f" + مكافأة {referral_bonus}"
        notification_text += "\n────────────────────\n"

    fancy_text = (
        f"{notification_text}"
        f"✨ مرحباً بك في البوت ✨\n\n"
        f"⭐ نقاطك: {user_points}\n"
        f"────────────────────\n"
        f"اختر الخدمة من الأزرار أدناه"
    )

    bot.send_message(chat_id, fancy_text, parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_force_sub")
def check_force_sub_callback(call):
    user_id = call.from_user.id
    if check_user_is_subscribed(user_id):
        bot.answer_callback_query(call.id, "✅ شكراً لاشتراكك!", show_alert=True)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        # ارسل له رسالة /start من جديد
        fake_msg = call.message
        fake_msg.from_user = call.from_user
        fake_msg.text = "/start"
        send_welcome(fake_msg)
    else:
        bot.answer_callback_query(call.id, "❌ لم تشترك بعد! اشترك ثم اضغط تحقق", show_alert=True)

# ======================
# 📞 دوال عرض الأرقام
# ======================

@bot.callback_query_handler(func=lambda call: call.data == "show_numbers_menu")
def show_numbers_menu(call):
    user_id = call.from_user.id

    if is_banned(user_id):
        bot.answer_callback_query(call.id, "🚫 محظور", show_alert=True)
        return

    if not is_admin(user_id) and is_force_sub_enabled():
        if not check_user_is_subscribed(user_id):
            bot.answer_callback_query(call.id, "⚠️ اشترك اولاً!", show_alert=True)
            bot.send_message(call.message.chat.id, "⚠️ يجب الاشتراك اولاً", reply_markup=get_force_sub_markup(), parse_mode="HTML")
            return

    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    all_combos = get_all_combos()

    country_combos = {}
    for country_code, combo_index in all_combos:
        if country_code not in country_combos:
            country_combos[country_code] = []
        country_combos[country_code].append(combo_index)

    for country_code, indices in country_combos.items():
        if country_code in COUNTRY_CODES:
            name, flag, _ = COUNTRY_CODES[country_code]
            for idx in indices:
                btn_text = f"{flag} {name}" if len(indices) == 1 else f"{flag} {name} ({idx})"
                buttons.append(types.InlineKeyboardButton(btn_text, callback_data=f"country_{country_code}_{idx}", style='primary'))

    for i in range(0, len(buttons), 2):
        markup.row(*buttons[i:i+2])

    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main", style='danger'))

    try:
        bot.edit_message_text(
            "🌍 اختر الدولة:",
            call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML"
        )
    except:
        bot.send_message(call.message.chat.id, "🌍 اختر الدولة:", reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith("country_"))
def handle_country_selection(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    if is_banned(user_id):
        bot.answer_callback_query(call.id, "🚫 محظور", show_alert=True)
        return

    parts = call.data.split("_")
    country_code = parts[1]
    combo_index = int(parts[2]) if len(parts) > 2 else 1

    available_numbers = get_available_numbers(country_code, combo_index, user_id)

    if not available_numbers:
        error_msg = "❌ جميع الأرقام قيد الاستخدام."
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="show_numbers_menu", style='primary'))
        try:
            bot.edit_message_text(error_msg, chat_id, call.message.message_id, reply_markup=markup, parse_mode="HTML")
        except:
            bot.send_message(chat_id, error_msg, reply_markup=markup, parse_mode="HTML")
        return

    assigned = random.choice(available_numbers)
    old_user = get_user(user_id)
    if old_user and old_user[5]:
        release_number(old_user[5])

    assign_number_to_user(user_id, assigned)
    save_user(user_id, country_code=country_code, assigned_number=assigned)

    name, flag, _ = COUNTRY_CODES.get(country_code, ("Unknown", "🌍", ""))

    msg_text = (
        f"📞 الرقم: <code>+{assigned}</code>\n"
        f"🌍 الدولة: {flag} {name}\n"
        f"⏳ في انتظار الرسائل"
    )
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("👥 قناة الأكواد", url="https://t.me/+oP-Hmxh2hYY0M2Y1",style='primary'),
        types.InlineKeyboardButton("🔄 تغيير الرقم", callback_data=f"change_num_{country_code}_{combo_index}", style='primary')
    )
    markup.row(
        types.InlineKeyboardButton("🗑️ حذف الرقم", callback_data=f"delete_this_number_{assigned}_{country_code}_{combo_index}", style='danger'),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="show_numbers_menu", style='primary')
    )

    try:
        bot.edit_message_text(msg_text, chat_id, call.message.message_id, reply_markup=markup, parse_mode="HTML")
        bot.answer_callback_query(call.id, "✅ تم تخصيص رقم")
    except Exception as e:
        print(f"Error: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_this_number_"))
def delete_current_number(call):
    parts = call.data.split("_")
    number = parts[3] if len(parts) > 3 else None
    country_code = parts[4] if len(parts) > 4 else None
    combo_index = int(parts[5]) if len(parts) > 5 else 1

    user_id = call.from_user.id

    if not number or not country_code:
        bot.answer_callback_query(call.id, "❌ خطأ في البيانات", show_alert=True)
        return

    if delete_combo_number(country_code, number, combo_index):
        release_number(number)
        bot.answer_callback_query(call.id, f"✅ تم حذف الرقم {number} من الكومبو", show_alert=True)
        show_numbers_menu(call)
    else:
        bot.answer_callback_query(call.id, "❌ فشل حذف الرقم", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith("change_num_"))
def change_number(call):
    user_id = call.from_user.id

    if is_banned(user_id):
        bot.answer_callback_query(call.id, "🚫 محظور", show_alert=True)
        return

    parts = call.data.split("_")
    country_code = parts[2]
    combo_index = int(parts[3]) if len(parts) > 3 else 1

    available_numbers = get_available_numbers(country_code, combo_index, user_id)

    if not available_numbers:
        bot.answer_callback_query(call.id, "❌ جميع الأرقام قيد الاستخدام", show_alert=True)
        return

    old_user = get_user(user_id)
    if old_user and old_user[5]:
        release_number(old_user[5])

    assigned = random.choice(available_numbers)
    assign_number_to_user(user_id, assigned)
    save_user(user_id, assigned_number=assigned)

    name, flag, _ = COUNTRY_CODES.get(country_code, ("Unknown", "🌍", ""))

    msg_text = (
        f"📞 الرقم: <code>+{assigned}</code>\n"
        f"🌍 الدولة: {flag} {name}\n"
        f"⏳ في انتظار الرسائل"
    )

    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("👥 قناة الأكواد", url="https://t.me/+oP-Hmxh2hYY0M2Y1",style='primary'),
        types.InlineKeyboardButton("🔄 تغيير الرقم", callback_data=f"change_num_{country_code}_{combo_index}", style='primary')
    )
    markup.row(
        types.InlineKeyboardButton("🗑️ حذف الرقم", callback_data=f"delete_this_number_{assigned}_{country_code}_{combo_index}", style='danger'),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="show_numbers_menu", style='primary')
    )

    try:
        bot.edit_message_text(msg_text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML")
        bot.answer_callback_query(call.id, "✅ تم تغيير الرقم")
    except Exception as e:
        print(f"Error: {e}")

# ======================
# 📁 دوال الملفات المدفوعة
# ======================

@bot.callback_query_handler(func=lambda call: call.data == "my_files_menu")
def my_files_menu(call):
    user_id = call.from_user.id

    if is_banned(user_id):
        bot.answer_callback_query(call.id, "🚫 محظور", show_alert=True)
        return

    if not is_admin(user_id) and is_force_sub_enabled():
        if not check_user_is_subscribed(user_id):
            bot.answer_callback_query(call.id, "⚠️ اشترك اولاً!", show_alert=True)
            bot.send_message(call.message.chat.id, "⚠️ يجب الاشتراك اولاً", reply_markup=get_force_sub_markup(), parse_mode="HTML")
            return

    purchased_files = get_user_purchased_files(user_id)

    if not purchased_files:
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.row(
            types.InlineKeyboardButton("الدول المتاحة 🔥", callback_data="files_store", style='primary'),
            types.InlineKeyboardButton("🎁 دعوة أصدقاء", callback_data="referral_menu", style='success')
        )
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main", style='danger'))
        try:
            bot.edit_message_text(
                "📁 <b>لا يوجد لديك ملفات مشتراة</b>\n\n"
                "يمكنك شراء ملفات من المتجر باستخدام نقاطك\n"
                "أو دعوة أصدقائك لكسب المزيد من النقاط!",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup,
                parse_mode="HTML"
            )
        except:
            bot.send_message(call.message.chat.id,
                "📁 <b>لا يوجد لديك ملفات مشتراة</b>\n\n"
                "يمكنك شراء ملفات من المتجر باستخدام نقاطك\n"
                "أو دعوة أصدقائك لكسب المزيد من النقاط!",
                reply_markup=markup,
                parse_mode="HTML"
            )
        return

    text = "📁 <b>ملفاتي المدفوعة</b>\n────────────────────\n"
    text += "<i>اختر الملف لعرض الأرقام:</i>\n\n"
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []

    for file in purchased_files:
        file_id, file_name, description, points, created_at, purchased_date = file
        buttons.append(types.InlineKeyboardButton(f"📄 {file_name}", callback_data=f"open_purchased_file_{file_id}", style='primary'))

    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            markup.row(buttons[i], buttons[i+1])
        else:
            markup.row(buttons[i])

    markup.row(
        types.InlineKeyboardButton("🛒 متجر الملفات", callback_data="files_store", style='success'),
        types.InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_to_main", style='danger')
    )

    try:
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML")
    except:
        bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith("open_purchased_file_"))
def open_purchased_file(call):
    file_id = int(call.data.split("_")[3])
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    if is_banned(user_id):
        bot.answer_callback_query(call.id, "🚫 محظور", show_alert=True)
        return

    if not has_user_purchased_file(user_id, file_id):
        bot.answer_callback_query(call.id, "❌ لم تشترِ هذا الملف بعد!", show_alert=True)
        return

    file_data = get_file_by_id(file_id)
    if not file_data:
        bot.answer_callback_query(call.id, "❌ الملف غير موجود!", show_alert=True)
        return

    numbers = file_data['numbers']

    if not numbers:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 رجوع للملفات", callback_data="my_files_menu", style='primary'))
        try:
            bot.edit_message_text(
                "<b>❌ لا توجد أرقام في هذا الملف!</b>",
                chat_id, call.message.message_id, reply_markup=markup, parse_mode="HTML"
            )
        except:
            bot.send_message(chat_id, "<b>❌ لا توجد أرقام في هذا الملف!</b>", reply_markup=markup, parse_mode="HTML")
        return

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT assigned_number FROM users WHERE assigned_number IS NOT NULL AND assigned_number!= ''")
    used_numbers = set(row[0] for row in c.fetchall())
    conn.close()

    available_numbers = [num for num in numbers if num not in used_numbers]

    if not available_numbers:
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.row(
            types.InlineKeyboardButton("🔄 محاولة مرة أخرى", callback_data=f"open_purchased_file_{file_id}", style='primary'),
            types.InlineKeyboardButton("🔙 رجوع للملفات", callback_data="my_files_menu", style='primary')
        )
        try:
            bot.edit_message_text(
                "<b>❌ جميع الأرقام في هذا الملف قيد الاستخدام حالياً.</b>\n\n"
                "<i>يمكنك المحاولة مرة أخرى أو حذف رقم مستخدم</i>",
                chat_id, call.message.message_id, reply_markup=markup, parse_mode="HTML"
            )
        except:
            bot.send_message(chat_id,
                "<b>❌ جميع الأرقام في هذا الملف قيد الاستخدام حالياً.</b>\n\n"
                "<i>يمكنك المحاولة مرة أخرى أو حذف رقم مستخدم</i>",
                reply_markup=markup, parse_mode="HTML"
            )
        return

    assigned = random.choice(available_numbers)

    old_user = get_user(user_id)
    if old_user and old_user[5]:
        release_number(old_user[5])

    assign_number_to_user(user_id, assigned)
    save_user(user_id, assigned_number=assigned)

    country_name, country_flag, _ = get_country_info(assigned)

    msg_text = (
        f"📞 <b>الرقم:</b> <code>+{assigned}</code>\n"
        f"🌍 <b>الدولة:</b> {country_flag} {country_name}\n"
        f"📁 <b>الملف:</b> {safe_html(file_data['file_name'])}\n"
        f"⭐ <b>نقاط الملف:</b> {file_data['points_required']}\n"
        f"⏳ <b>الحالة:</b> في انتظار الرسائل"
    )

    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("👥 قناة الأكواد", url="https://t.me/+oP-Hmxh2hYY0M2Y1",style='primary'),
        types.InlineKeyboardButton("🔄 تغيير الرقم", callback_data=f"change_purchased_num_{file_id}", style='primary')
    )
    markup.row(
        types.InlineKeyboardButton("🗑️ حذف الرقم", callback_data=f"delete_purchased_number_{assigned}_{file_id}", style='danger'),
        types.InlineKeyboardButton("🔙 رجوع للملفات", callback_data="my_files_menu", style='primary')
    )

    try:
        bot.edit_message_text(
            text=msg_text,
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=markup,
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        bot.answer_callback_query(call.id, "✅ تم تخصيص رقم لك")
    except Exception as e:
        print(f"Error in open_purchased_file: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("change_purchased_num_"))
def change_purchased_number(call):
    user_id = call.from_user.id
    file_id = int(call.data.split("_")[3])

    if is_banned(user_id):
        bot.answer_callback_query(call.id, "🚫 محظور", show_alert=True)
        return

    if not has_user_purchased_file(user_id, file_id):
        bot.answer_callback_query(call.id, "❌ لم تشترِ هذا الملف بعد!", show_alert=True)
        return

    file_data = get_file_by_id(file_id)
    if not file_data:
        bot.answer_callback_query(call.id, "❌ الملف غير موجود!", show_alert=True)
        return

    numbers = file_data['numbers']

    if not numbers:
        bot.answer_callback_query(call.id, "❌ لا توجد أرقام في هذا الملف!", show_alert=True)
        return

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT assigned_number FROM users WHERE assigned_number IS NOT NULL AND assigned_number!= ''")
    used_numbers = set(row[0] for row in c.fetchall())
    conn.close()

    available_numbers = [num for num in numbers if num not in used_numbers]

    if not available_numbers:
        bot.answer_callback_query(call.id, "❌ جميع الأرقام قيد الاستخدام حالياً.", show_alert=True)
        return

    old_user = get_user(user_id)
    if old_user and old_user[5]:
        release_number(old_user[5])

    assigned = random.choice(available_numbers)
    assign_number_to_user(user_id, assigned)
    save_user(user_id, assigned_number=assigned)

    country_name, country_flag, _ = get_country_info(assigned)

    msg_text = (
        f"📞 <b>الرقم:</b> <code>+{assigned}</code>\n"
        f"🌍 <b>الدولة:</b> {country_flag} {country_name}\n"
        f"📁 <b>الملف:</b> {safe_html(file_data['file_name'])}\n"
        f"⭐ <b>نقاط الملف:</b> {file_data['points_required']}\n"
        f"⏳ <b>الحالة:</b> في انتظار الرسائل"
    )

    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("👥 قناة الأكواد", url="https://t.me/+oP-Hmxh2hYY0M2Y1",style='primary'),
        types.InlineKeyboardButton("🔄 تغيير الرقم", callback_data=f"change_purchased_num_{file_id}", style='primary')
    )
    markup.row(
        types.InlineKeyboardButton("🗑️ حذف الرقم", callback_data=f"delete_purchased_number_{assigned}_{file_id}", style='danger'),
        types.InlineKeyboardButton("🔙 رجوع للملفات", callback_data="my_files_menu", style='primary')
    )

    try:
        bot.edit_message_text(
            text=msg_text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup,
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        bot.answer_callback_query(call.id, "✅ تم تغيير الرقم")
    except Exception as e:
        print(f"Error: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_purchased_number_"))
def delete_purchased_number(call):
    parts = call.data.split("_")
    number = parts[3] if len(parts) > 3 else None
    file_id = int(parts[4]) if len(parts) > 4 else None

    user_id = call.from_user.id

    if not number or not file_id:
        bot.answer_callback_query(call.id, "❌ خطأ", show_alert=True)
        return

    file_data = get_file_by_id(file_id)
    if not file_data:
        bot.answer_callback_query(call.id, "❌ الملف غير موجود", show_alert=True)
        return

    numbers = file_data['numbers']
    if number in numbers:
        numbers.remove(number)

        with db_lock:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("UPDATE files_lists SET numbers =? WHERE id =?", (json.dumps(numbers), file_id))
            conn.commit()
            conn.close()

        release_number(number)
        bot.answer_callback_query(call.id, f"✅ تم حذف الرقم {number}", show_alert=True)
        open_purchased_file(call)
    else:
        bot.answer_callback_query(call.id, "❌ الرقم غير موجود", show_alert=True)

# ======================
# 🛒 متجر الملفات
# ======================

@bot.callback_query_handler(func=lambda call: call.data == "files_store")
def files_store(call):
    user_id = call.from_user.id
    user_points = get_user_points(user_id)
    files = get_all_files()

    purchased_files = get_user_purchased_files(user_id)
    purchased_ids = [f[0] for f in purchased_files]

    available_files = [f for f in files if f[0] not in purchased_ids]

    if not available_files:
        text = (
            f"📚 <b>متجر الملفات</b>\n"
            f"⭐ رصيدك: {user_points} نقطة\n"
            f"────────────────────\n\n"
            f"✅ لقد اشتريت جميع الملفات المتاحة!\n"
            f"سيتم إضافة ملفات جديدة قريباً."
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="my_files_menu", style='primary'))
        try:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML")
        except:
            bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode="HTML")
        return

    text = f"📚 <b>متجر الملفات</b>\n⭐ رصيدك: {user_points} نقطة\n────────────────────\n\n"
    markup = types.InlineKeyboardMarkup(row_width=1)

    for file in available_files:
        file_id, file_name, description, points_required, created_by, created_at = file
        text += f"📄 <b>{safe_html(file_name)}</b>\n"
        text += f"📝 {safe_html(description[:60])}\n"
        text += f"⭐ {points_required} نقطة\n────────────────────\n"
        markup.add(types.InlineKeyboardButton(f"💰 شراء {file_name} ({points_required} نقطة)", callback_data=f"buy_file_{file_id}", style='success'))

    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="my_files_menu", style='danger'))

    try:
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML")
    except:
        bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_file_"))
def buy_file(call):
    file_id = int(call.data.split("_")[2])
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    if is_banned(user_id):
        bot.answer_callback_query(call.id, "🚫 محظور", show_alert=True)
        return

    result, status = purchase_file(user_id, file_id)

    if status == "success":
        file_data = get_file_by_id(file_id)
        bot.answer_callback_query(call.id, f"✅ تم شراء {file_data['file_name']} بنجاح!", show_alert=True)

        numbers = file_data['numbers']

        if not numbers:
            bot.send_message(chat_id, "❌ لا توجد أرقام في هذا الملف!")
            return

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT assigned_number FROM users WHERE assigned_number IS NOT NULL AND assigned_number!= ''")
        used_numbers = set(row[0] for row in c.fetchall())
        conn.close()

        available_numbers = [num for num in numbers if num not in used_numbers]

        if not available_numbers:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 رجوع للملفات", callback_data="my_files_menu", style='primary'))
            try:
                bot.edit_message_text(
                    "❌ جميع الأرقام في هذا الملف قيد الاستخدام حالياً.",
                    chat_id, call.message.message_id, reply_markup=markup, parse_mode="HTML"
                )
            except:
                bot.send_message(chat_id, "❌ جميع الأرقام في هذا الملف قيد الاستخدام حالياً.", reply_markup=markup)
            return

        assigned = random.choice(available_numbers)

        old_user = get_user(user_id)
        if old_user and old_user[5]:
            release_number(old_user[5])

        assign_number_to_user(user_id, assigned)
        save_user(user_id, assigned_number=assigned)

        country_name, country_flag, _ = get_country_info(assigned)

        msg_text = (
            f"📞 <b>الرقم:</b> <code>+{assigned}</code>\n"
            f"🌍 <b>الدولة:</b> {country_flag} {country_name}\n"
            f"📁 <b>الملف:</b> {safe_html(file_data['file_name'])}\n"
            f"⭐ <b>نقاط الملف:</b> {file_data['points_required']}\n"
            f"⏳ <b>الحالة:</b> في انتظار الرسائل"
        )

        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("👥 ؤ الأكواد", url="https://t.me/+DjosrAcgW8A2ZTNk",style='primary'),
            types.InlineKeyboardButton("🔄 تغيير الرقم", callback_data=f"change_purchased_num_{file_id}", style='primary')
        )
        markup.row(
            types.InlineKeyboardButton("🗑️ حذف الرقم", callback_data=f"delete_purchased_number_{assigned}_{file_id}", style='danger'),
            types.InlineKeyboardButton("🔙 رجوع للملفات", callback_data="my_files_menu", style='primary')
        )

        try:
            bot.edit_message_text(
                text=msg_text,
                chat_id=chat_id,
                message_id=call.message.message_id,
                reply_markup=markup,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
        except:
            bot.send_message(chat_id, msg_text, reply_markup=markup, parse_mode="HTML")

    elif status == "already_purchased":
        bot.answer_callback_query(call.id, "❌ لقد اشتريت هذا الملف بالفعل!", show_alert=True)
    elif status == "insufficient_points":
        bot.answer_callback_query(call.id, f"❌ نقاطك غير كافية! رصيدك: {get_user_points(user_id)} نقطة", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "❌ حدث خطأ، حاول مرة أخرى.", show_alert=True)

# ======================
# 🏆 دوال النقاط والدعوات
# ======================

@bot.callback_query_handler(func=lambda call: call.data == "show_points")
def show_points(call):
    user_id = call.from_user.id
    points = get_user_points(user_id)
    invites = get_user_invites_count(user_id)

    text = (
        f"🏆 رصيد نقاطك\n────────────────────\n"
        f"⭐ {points} نقطة\n\n"
        f"👥 عدد المدعوين: {invites}\n"
        f"🎁 كل دعوة = {REFERRAL_POINTS} نقطة\n"
        f"🎉 مكافأة كل 5 دعوات = {INVITE_BONUS} نقطة"
    )

    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("🎁 دعوة أصدقاء", callback_data="referral_menu", style='success'),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main", style='danger')
    )

    try:
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML")
    except:
        bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "referral_menu")
def referral_menu(call):
    user_id = call.from_user.id
    points = get_user_points(user_id)
    invites = get_user_invites_count(user_id)

    invite_link = f"https://t.me/{bot.get_me().username}?start={user_id}"

    text = (
        f"🎁 نظام الدعوات\n────────────────────\n"
        f"⭐ نقاطك: {points}\n"
        f"👥 عدد المدعوين: {invites}\n\n"
        f"رابط دعوتك:\n<code>{invite_link}</code>\n\n"
        f"💰 كل مدعو يمنحك {REFERRAL_POINTS} نقطة\n"
        f"🎁 مكافأة {INVITE_BONUS} نقطة عند كل 5 دعوات"
    )

    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("👥 قائمة المدعوين", callback_data="invites_list", style='primary'),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main", style='danger')
    )

    try:
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML")
    except:
        bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "invites_list")
def invites_list(call):
    user_id = call.from_user.id
    invites = get_invites_list(user_id)

    if not invites:
        text = "👥 لا يوجد لديك دعوات بعد!"
    else:
        text = "👥 قائمة المدعوين:\n────────────────────\n"
        for referred_id, username, first_name, date in invites:
            name = f"@{username}" if username else first_name or str(referred_id)
            text += f"• {name}\n 📅 {date}\n"

    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("🎁 رابط الدعوة", callback_data="referral_menu", style='success'),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main", style='danger')
    )

    try:
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML")
    except:
        bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode="HTML")

# ======================
# 🔙 دوال الرجوع
# ======================

@bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
def back_to_main(call):
    send_welcome(call.message)

# ======================
# 🔐 لوحة التحكم للمطور
# ======================

user_states = {}

def admin_main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    status_icon = "🟢" if not is_maintenance_mode() else "🔴"
    status_text = "يعمل" if not is_maintenance_mode() else "صيانة"
    force_status = "🔒 مفعل" if is_force_sub_enabled() else "🔓 معطل"
    markup.add(types.InlineKeyboardButton(f"{status_icon} {status_text}", callback_data="toggle_maintenance", style='primary'),
               types.InlineKeyboardButton(f"{force_status} اشتراك", callback_data="toggle_force_sub", style='primary'))
    markup.row(
        types.InlineKeyboardButton("📥 إضافة كومبو", callback_data="admin_add_combo", style='primary'),
        types.InlineKeyboardButton("🗑️ حذف كومبو", callback_data="admin_del_combo", style='danger')
    )
    markup.row(
        types.InlineKeyboardButton("📁 إدارة الملفات", callback_data="admin_files_menu", style='primary'),
        types.InlineKeyboardButton("🏆 إدارة النقاط", callback_data="admin_points_menu", style='primary')
    )
    markup.row(
        types.InlineKeyboardButton("📢 قنوات الاشتراك", callback_data="admin_force_sub_menu", style='primary'),
        types.InlineKeyboardButton("📊 الإحصائيات", callback_data="admin_stats", style='primary')
    )
    markup.row(
        types.InlineKeyboardButton("📢 إذاعة", callback_data="admin_broadcast", style='success'),
        types.InlineKeyboardButton("🚫 حظر", callback_data="admin_ban", style='danger')
    )
    markup.row(
        types.InlineKeyboardButton("✅ إلغاء حظر", callback_data="admin_unban", style='success'),
        types.InlineKeyboardButton("💾 نسخ احتياطي", callback_data="admin_backup", style='primary')
    )
    markup.row(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main", style='danger'))
    return markup

@bot.callback_query_handler(func=lambda call: call.data == "admin_panel")
def show_admin_panel(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "⚠️ للمطورين فقط", show_alert=True)
        return

    total_users = len(get_all_users())
    admin_text = f"👋 مرحباً مطور\n────────────────────\n👥 المستخدمين: {total_users}\n🕐 الوقت: {datetime.now().strftime('%H:%M:%S')}"

    try:
        bot.edit_message_text(admin_text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=admin_main_menu())
    except:
        bot.send_message(call.message.chat.id, admin_text, parse_mode="HTML", reply_markup=admin_main_menu())

@bot.callback_query_handler(func=lambda call: call.data == "toggle_force_sub")
def handle_force_sub_toggle(call):
    if not is_admin(call.from_user.id):
        return
    new_status = toggle_force_sub()
    bot.answer_callback_query(call.id, f"✅ الاشتراك الاجباري {'مفعل' if new_status else 'معطل'}")
    show_admin_panel(call)

@bot.callback_query_handler(func=lambda call: call.data == "admin_force_sub_menu")
def admin_force_sub_menu(call):
    if not is_admin(call.from_user.id):
        return
    channels = get_all_force_sub_channels_admin()
    text = f"🔒 <b>ادارة الاشتراك الاجباري</b>\nالحالة: {'🟢 مفعل' if is_force_sub_enabled() else '🔴 معطل'}\n────────────────────\n"
    if not channels:
        text += "لا توجد قنوات مضافة"
    else:
        for cid, url, en in channels:
            text += f"\n🆔 {cid} | @{parse_channel_username(url)} | {'✅' if en else '❌'}"
    text += "\n\n⚠️ مهم: يجب ان يكون البوت ادمن في القناة حتى يعمل الفحص!"

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton("➕ اضافة قناة", callback_data="admin_add_force_channel", style='success'),
        types.InlineKeyboardButton("🗑️ حذف قناة", callback_data="admin_del_force_channel", style='danger')
    )
    markup.row(
        types.InlineKeyboardButton(f"{'🔓 تعطيل' if is_force_sub_enabled() else '🔒 تفعيل'} الاشتراك", callback_data="toggle_force_sub", style='primary'),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel", style='primary')
    )
    try:
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML")
    except:
        bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "admin_add_force_channel")
def admin_add_force_channel_step1(call):
    if not is_admin(call.from_user.id):
        return
    user_states[call.from_user.id] = "waiting_force_channel"
    try:
        bot.edit_message_text("📢 ارسل معرف القناة او رابطها\n\nمثال:\n@MyChannel\nhttps://t.me/MyChannel", call.message.chat.id, call.message.message_id)
    except:
        bot.send_message(call.message.chat.id, "📢 ارسل معرف القناة او رابطها")

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "waiting_force_channel" and is_admin(msg.from_user.id))
def admin_add_force_channel_step2(message):
    channel = message.text.strip()
    if add_force_sub_channel(channel):
        bot.reply_to(message, f"✅ تم اضافة القناة: {channel}")
    else:
        bot.reply_to(message, "❌ القناة موجودة مسبقاً او خطأ في الاضافة")
    del user_states[message.from_user.id]

@bot.callback_query_handler(func=lambda call: call.data == "admin_del_force_channel")
def admin_del_force_channel_menu(call):
    if not is_admin(call.from_user.id):
        return
    channels = get_all_force_sub_channels_admin()
    if not channels:
        bot.answer_callback_query(call.id, "لا توجد قنوات", show_alert=True)
        return
    markup = types.InlineKeyboardMarkup(row_width=1)
    for cid, url, en in channels:
        markup.add(types.InlineKeyboardButton(f"🗑️ {parse_channel_username(url)}", callback_data=f"del_force_{cid}", style='danger'))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_force_sub_menu", style='primary'))
    try:
        bot.edit_message_text("اختر القناة للحذف:", call.message.chat.id, call.message.message_id, reply_markup=markup)
    except:
        bot.send_message(call.message.chat.id, "اختر القناة للحذف:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("del_force_"))
def confirm_del_force_channel(call):
    if not is_admin(call.from_user.id):
        return
    cid = int(call.data.split("_")[2])
    delete_force_sub_channel(cid)
    bot.answer_callback_query(call.id, "✅ تم الحذف")
    admin_force_sub_menu(call)

@bot.callback_query_handler(func=lambda call: call.data == "admin_backup")
def admin_backup(call):
    if not is_admin(call.from_user.id):
        return

    if backup_users_to_file():
        bot.answer_callback_query(call.id, "✅ تم إنشاء نسخة احتياطية للمستخدمين", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "❌ فشل إنشاء النسخة الاحتياطية", show_alert=True)

# ======================
# 📁 إدارة الملفات (للأدمن)
# ======================

@bot.callback_query_handler(func=lambda call: call.data == "admin_files_menu")
def admin_files_menu(call):
    if not is_admin(call.from_user.id):
        return

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton("➕ إضافة ملف جديد", callback_data="admin_add_file_simple", style='success'),
        types.InlineKeyboardButton("📋 قائمة الملفات", callback_data="admin_list_files", style='primary')
    )
    markup.row(
        types.InlineKeyboardButton("🗑️ حذف ملف", callback_data="admin_delete_file", style='danger'),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel", style='primary')
    )

    try:
        bot.edit_message_text(
            "📁 <b>إدارة الملفات</b>\n"
            "────────────────────\n"
            "• أرسل ملف TXT يحتوي على الأرقام\n"
            "• سيتم التعرف على الدولة تلقائياً من أول رقم\n"
            "• ثم سيطلب منك عدد النقاط المطلوبة",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup,
            parse_mode="HTML"
        )
    except:
        bot.send_message(call.message.chat.id,
            "📁 <b>إدارة الملفات</b>\n"
            "────────────────────\n"
            "• أرسل ملف TXT يحتوي على الأرقام\n"
            "• سيتم التعرف على الدولة تلقائياً من أول رقم\n"
            "• ثم سيطلب منك عدد النقاط المطلوبة",
            reply_markup=markup,
            parse_mode="HTML"
        )

@bot.callback_query_handler(func=lambda call: call.data == "admin_add_file_simple")
def admin_add_file_simple(call):
    if not is_admin(call.from_user.id):
        return
    user_states[call.from_user.id] = "waiting_file_simple"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_files_menu", style='danger'))
    try:
        bot.edit_message_text(
            "📤 <b>إضافة ملف جديد</b>\n"
            "────────────────────\n"
            "أرسل ملف TXT يحتوي على الأرقام (رقم واحد في كل سطر)\n\n"
            "<i>مثال:\n+201234567890\n+201234567891\n+201234567892</i>\n\n"
            "سيتم التعرف على الدولة تلقائياً من أول رقم",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup,
            parse_mode="HTML"
        )
    except:
        bot.send_message(call.message.chat.id,
            "📤 <b>إضافة ملف جديد</b>\n"
            "────────────────────\n"
            "أرسل ملف TXT يحتوي على الأرقام (رقم واحد في كل سطر)\n\n"
            "<i>مثال:\n+201234567890\n+201234567891\n+201234567892</i>\n\n"
            "سيتم التعرف على الدولة تلقائياً من أول رقم",
            reply_markup=markup,
            parse_mode="HTML"
        )

@bot.message_handler(content_types=['document'], func=lambda msg: user_states.get(msg.from_user.id) == "waiting_file_simple" and is_admin(msg.from_user.id))
def admin_add_file_simple_step2(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        content = downloaded_file.decode('utf-8')
        numbers = [line.strip() for line in content.splitlines() if line.strip()]

        if not numbers:
            bot.reply_to(message, "❌ الملف فارغ! أرسل ملفاً يحتوي على أرقام.")
            return

        first_num = clean_number(numbers[0])
        country_code = None
        country_name = None
        country_flag = None

        for code, (name, flag, short) in COUNTRY_CODES.items():
            if first_num.startswith(code):
                country_code = code
                country_name = name
                country_flag = flag
                break

        if not country_code:
            markup = types.InlineKeyboardMarkup()
            buttons = []
            for code, (name, flag, short) in list(COUNTRY_CODES.items())[:20]:
                buttons.append(types.InlineKeyboardButton(f"{flag} {name}", callback_data=f"set_country_{code}_{message.from_user.id}", style='primary'))

            for i in range(0, len(buttons), 2):
                if i + 1 < len(buttons):
                    markup.row(buttons[i], buttons[i+1])
                else:
                    markup.row(buttons[i])

            markup.add(types.InlineKeyboardButton("🔙 إلغاء", callback_data="admin_files_menu", style='danger'))

            user_states[message.from_user.id] = {
                "step": "waiting_country_selection",
                "numbers": numbers,
                "temp_numbers": numbers
            }

            bot.reply_to(
                message,
                f"⚠️ <b>لم نتمكن من تحديد الدولة تلقائياً</b>\n"
                f"────────────────────\n"
                f"أول رقم في الملف: <code>{first_num}</code>\n\n"
                f"الرجاء اختيار الدولة من الأزرار أدناه:",
                reply_markup=markup,
                parse_mode="HTML"
            )
            return

        user_states[message.from_user.id] = {
            "step": "waiting_points_for_file",
            "numbers": numbers,
            "file_name": f"{country_flag} {country_name}",
            "description": f"أرقام {country_name} - {len(numbers)} رقم"
        }

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 إلغاء", callback_data="admin_files_menu", style='danger'))

        bot.reply_to(
            message,
            f"✅ <b>تم التعرف على الملف</b>\n"
            f"────────────────────\n"
            f"🌍 <b>الدولة:</b> {country_flag} {country_name}\n"
            f"🔢 <b>عدد الأرقام:</b> {len(numbers)}\n"
            f"────────────────────\n"
            f"⭐ <b>الآن أدخل عدد النقاط المطلوبة لفتح هذا الملف:</b>\n"
            f"<i>(الافتراضي: {DEFAULT_POINTS_TO_UNLOCK} نقاط)</i>",
            reply_markup=markup,
            parse_mode="HTML"
        )

    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ: {str(e)}")
        traceback.print_exc()
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]

@bot.callback_query_handler(func=lambda call: call.data.startswith("set_country_"))
def set_country_for_file(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
        return

    parts = call.data.split("_")
    country_code = parts[2]
    admin_id = int(parts[3])

    if call.from_user.id!= admin_id:
        bot.answer_callback_query(call.id, "❌ هذا الإجراء لمستخدم آخر", show_alert=True)
        return

    state_data = user_states.get(call.from_user.id)
    if not state_data or not isinstance(state_data, dict):
        bot.answer_callback_query(call.id, "❌ انتهت الجلسة، ابدأ من جديد", show_alert=True)
        return

    numbers = state_data.get("numbers", [])
    country_name, country_flag, _ = COUNTRY_CODES.get(country_code, ("Unknown", "🌍", ""))

    user_states[call.from_user.id] = {
        "step": "waiting_points_for_file",
        "numbers": numbers,
        "file_name": f"{country_flag} {country_name}",
        "description": f"أرقام {country_name} - {len(numbers)} رقم"
    }

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 إلغاء", callback_data="admin_files_menu", style='danger'))

    try:
        bot.edit_message_text(
            f"✅ <b>تم تعيين الدولة</b>\n"
            f"────────────────────\n"
            f"🌍 <b>الدولة:</b> {country_flag} {country_name}\n"
            f"🔢 <b>عدد الأرقام:</b> {len(numbers)}\n"
            f"────────────────────\n"
            f"⭐ <b>الآن أدخل عدد النقاط المطلوبة لفتح هذا الملف:</b>\n"
            f"<i>(الافتراضي: {DEFAULT_POINTS_TO_UNLOCK} نقاط)</i>",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup,
            parse_mode="HTML"
        )
    except:
        bot.send_message(call.message.chat.id,
            f"✅ <b>تم تعيين الدولة</b>\n"
            f"────────────────────\n"
            f"🌍 <b>الدولة:</b> {country_flag} {country_name}\n"
            f"🔢 <b>عدد الأرقام:</b> {len(numbers)}\n"
            f"────────────────────\n"
            f"⭐ <b>الآن أدخل عدد النقاط المطلوبة لفتح هذا الملف:</b>\n"
            f"<i>(الافتراضي: {DEFAULT_POINTS_TO_UNLOCK} نقاط)</i>",
            reply_markup=markup,
            parse_mode="HTML"
        )

@bot.message_handler(func=lambda msg: isinstance(user_states.get(msg.from_user.id), dict) and user_states[msg.from_user.id].get("step") == "waiting_points_for_file" and is_admin(msg.from_user.id))
def admin_add_file_set_points(message):
    try:
        points = int(message.text.strip())
        if points < 1:
            points = DEFAULT_POINTS_TO_UNLOCK
    except:
        points = DEFAULT_POINTS_TO_UNLOCK

    data = user_states[message.from_user.id]
    numbers = data["numbers"]
    file_name = data["file_name"]
    description = data["description"]

    file_id = add_file_list(
        file_name=file_name,
        description=description,
        numbers=numbers,
        points_required=points,
        created_by=message.from_user.id
    )

    bot.reply_to(
        message,
        f"✅ <b>تم إضافة الملف بنجاح!</b>\n"
        f"────────────────────\n"
        f"📄 <b>الاسم:</b> {safe_html(file_name)}\n"
        f"📝 <b>الوصف:</b> {safe_html(description)}\n"
        f"⭐ <b>النقاط المطلوبة:</b> {points}\n"
        f"🔢 <b>عدد الأرقام:</b> {len(numbers)}\n"
        f"🆔 <b>معرف الملف:</b> {file_id}",
        parse_mode="HTML"
    )

    del user_states[message.from_user.id]

@bot.callback_query_handler(func=lambda call: call.data == "admin_list_files")
def admin_list_files(call):
    if not is_admin(call.from_user.id):
        return

    files = get_all_files()

    if not files:
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.row(
            types.InlineKeyboardButton("➕ إضافة ملف", callback_data="admin_add_file_simple", style='success'),
            types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_files_menu", style='primary')
        )
        try:
            bot.edit_message_text(
                "📋 <b>لا توجد ملفات حالياً</b>",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup,
                parse_mode="HTML"
            )
        except:
            bot.send_message(call.message.chat.id, "📋 <b>لا توجد ملفات حالياً</b>", reply_markup=markup, parse_mode="HTML")
        return

    text = "📋 <b>قائمة الملفات</b>\n────────────────────\n"
    for file in files:
        file_id, file_name, description, points, created_by, created_at = file
        text += f"\n📄 <b>{safe_html(file_name)}</b>\n"
        text += f"📝 {safe_html(description[:40])}\n"
        text += f"⭐ {points} نقطة\n"
        text += f"🆔 ID: {file_id}\n"
        text += "────────────────────\n"

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton("➕ إضافة ملف", callback_data="admin_add_file_simple", style='success'),
        types.InlineKeyboardButton("🗑️ حذف ملف", callback_data="admin_delete_file", style='danger')
    )
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_files_menu", style='primary'))

    try:
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML")
    except:
        bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "admin_delete_file")
def admin_delete_file(call):
    if not is_admin(call.from_user.id):
        return

    files = get_all_files()

    if not files:
        bot.answer_callback_query(call.id, "❌ لا توجد ملفات للحذف", show_alert=True)
        return

    markup = types.InlineKeyboardMarkup(row_width=1)
    for file in files:
        file_id, file_name, description, points, _, _ = file
        markup.add(types.InlineKeyboardButton(f"🗑️ {file_name} ({points} نقطة)", callback_data=f"confirm_delete_file_{file_id}", style='danger'))

    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_files_menu", style='primary'))

    try:
        bot.edit_message_text(
            "🗑️ <b>اختر الملف للحذف:</b>",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup,
            parse_mode="HTML"
        )
    except:
        bot.send_message(call.message.chat.id, "🗑️ <b>اختر الملف للحذف:</b>", reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_delete_file_"))
def confirm_delete_file(call):
    if not is_admin(call.from_user.id):
        return

    try:
        file_id = int(call.data.split("_")[3])
        file_data = get_file_by_id(file_id)

        if file_data:
            delete_file_permanently(file_id)
            bot.answer_callback_query(call.id, f"✅ تم حذف {file_data['file_name']} نهائياً", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "❌ الملف غير موجود", show_alert=True)

        admin_files_menu(call)

    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ خطأ: {str(e)[:50]}", show_alert=True)
        print(f"Error in confirm_delete_file: {e}")

# ======================
# 🏆 إدارة النقاط للمطور
# ======================

@bot.callback_query_handler(func=lambda call: call.data == "admin_points_menu")
def admin_points_menu(call):
    if not is_admin(call.from_user.id):
        return
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton("➕ إضافة نقاط", callback_data="admin_add_points", style='success'),
        types.InlineKeyboardButton("➖ خصم نقاط", callback_data="admin_remove_points", style='danger')
    )
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel", style='primary'))
    try:
        bot.edit_message_text("🏆 <b>إدارة النقاط</b>", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML")
    except:
        bot.send_message(call.message.chat.id, "🏆 <b>إدارة النقاط</b>", reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "admin_add_points")
def admin_add_points_step1(call):
    if not is_admin(call.from_user.id):
        return
    user_states[call.from_user.id] = "add_points_user"
    try:
        bot.edit_message_text("أرسل معرف المستخدم:", call.message.chat.id, call.message.message_id)
    except:
        bot.send_message(call.message.chat.id, "أرسل معرف المستخدم:")

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "add_points_user" and is_admin(msg.from_user.id))
def admin_add_points_step2(message):
    try:
        user_id = int(message.text.strip())
        user_states[message.from_user.id] = f"add_points_amount_{user_id}"
        bot.reply_to(message, "أرسل عدد النقاط:")
    except:
        bot.reply_to(message, "❌ معرف غير صحيح")

@bot.message_handler(func=lambda msg: isinstance(user_states.get(msg.from_user.id), str) and user_states[msg.from_user.id].startswith("add_points_amount_") and is_admin(msg.from_user.id))
def admin_add_points_step3(message):
    try:
        user_id = int(user_states[message.from_user.id].split("_")[3])
        points = int(message.text.strip())
        if points <= 0:
            bot.reply_to(message, "❌ نقاط موجبة")
            return
        add_points(user_id, points, f"إضافة من الأدمن")
        bot.reply_to(message, f"✅ تم إضافة {points} نقطة للمستخدم {user_id}")
    except:
        bot.reply_to(message, "❌ خطأ")
    del user_states[message.from_user.id]

@bot.callback_query_handler(func=lambda call: call.data == "admin_remove_points")
def admin_remove_points_step1(call):
    if not is_admin(call.from_user.id):
        return
    user_states[call.from_user.id] = "remove_points_user"
    try:
        bot.edit_message_text("أرسل معرف المستخدم:", call.message.chat.id, call.message.message_id)
    except:
        bot.send_message(call.message.chat.id, "أرسل معرف المستخدم:")

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "remove_points_user" and is_admin(msg.from_user.id))
def admin_remove_points_step2(message):
    try:
        user_id = int(message.text.strip())
        user_states[message.from_user.id] = f"remove_points_amount_{user_id}"
        bot.reply_to(message, "أرسل عدد النقاط للخصم:")
    except:
        bot.reply_to(message, "❌ معرف غير صحيح")

@bot.message_handler(func=lambda msg: isinstance(user_states.get(msg.from_user.id), str) and user_states[msg.from_user.id].startswith("remove_points_amount_") and is_admin(msg.from_user.id))
def admin_remove_points_step3(message):
    try:
        user_id = int(user_states[message.from_user.id].split("_")[3])
        points = int(message.text.strip())
        if points <= 0:
            bot.reply_to(message, "❌ نقاط موجبة")
            return
        if deduct_points(user_id, points):
            bot.reply_to(message, f"✅ تم خصم {points} نقطة من المستخدم {user_id}")
        else:
            bot.reply_to(message, "❌ رصيد غير كافٍ")
    except:
        bot.reply_to(message, "❌ خطأ")
    del user_states[message.from_user.id]

# ======================
# 📊 الإحصائيات
# ======================

@bot.callback_query_handler(func=lambda call: call.data == "admin_stats")
def admin_stats(call):
    if not is_admin(call.from_user.id):
        return
    total_users = len(get_all_users())
    total_files = len(get_all_files())
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT SUM(points) FROM users")
    total_points = c.fetchone()[0] or 0
    conn.close()
    text = f"📊 <b>الإحصائيات</b>\n────────────────────\n👥 المستخدمين: {total_users}\n📁 الملفات: {total_files}\n⭐ إجمالي النقاط: {total_points}"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel", style='primary'))
    try:
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML")
    except:
        bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode="HTML")

# ======================
# 📢 الإذاعة
# ======================

@bot.callback_query_handler(func=lambda call: call.data == "admin_broadcast")
def admin_broadcast_step1(call):
    if not is_admin(call.from_user.id):
        return
    user_states[call.from_user.id] = "broadcast_msg"
    try:
        bot.edit_message_text("أرسل الرسالة للإذاعة:", call.message.chat.id, call.message.message_id)
    except:
        bot.send_message(call.message.chat.id, "أرسل الرسالة للإذاعة:")

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "broadcast_msg" and is_admin(msg.from_user.id))
def admin_broadcast_step2(message):
    users = get_all_users()
    success = 0
    for uid in users:
        try:
            bot.send_message(uid, message.text)
            success += 1
        except:
            pass
    bot.reply_to(message, f"✅ تم الإرسال إلى {success}/{len(users)} مستخدم")
    del user_states[message.from_user.id]

# ======================
# 🚫 الحظر وإلغاء الحظر
# ======================

@bot.callback_query_handler(func=lambda call: call.data == "admin_ban")
def admin_ban_step1(call):
    if not is_admin(call.from_user.id):
        return
    user_states[call.from_user.id] = "ban_user"
    try:
        bot.edit_message_text("أرسل معرف المستخدم للحظر:", call.message.chat.id, call.message.message_id)
    except:
        bot.send_message(call.message.chat.id, "أرسل معرف المستخدم للحظر:")

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "ban_user" and is_admin(msg.from_user.id))
def admin_ban_step2(message):
    try:
        uid = int(message.text)
        ban_user(uid)
        bot.reply_to(message, f"✅ تم حظر {uid}")
    except:
        bot.reply_to(message, "❌ معرف غير صحيح")
    del user_states[message.from_user.id]

@bot.callback_query_handler(func=lambda call: call.data == "admin_unban")
def admin_unban_step1(call):
    if not is_admin(call.from_user.id):
        return
    user_states[call.from_user.id] = "unban_user"
    try:
        bot.edit_message_text("أرسل معرف المستخدم لإلغاء الحظر:", call.message.chat.id, call.message.message_id)
    except:
        bot.send_message(call.message.chat.id, "أرسل معرف المستخدم لإلغاء الحظر:")

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "unban_user" and is_admin(msg.from_user.id))
def admin_unban_step2(message):
    try:
        uid = int(message.text)
        unban_user(uid)
        bot.reply_to(message, f"✅ تم إلغاء حظر {uid}")
    except:
        bot.reply_to(message, "❌ معرف غير صحيح")
    del user_states[message.from_user.id]

@bot.callback_query_handler(func=lambda call: call.data == "toggle_maintenance")
def handle_maintenance_toggle(call):
    if not is_admin(call.from_user.id):
        return
    current = is_maintenance_mode()
    set_maintenance_mode(not current)
    bot.answer_callback_query(call.id, "✅ تم تغيير حالة الصيانة")
    show_admin_panel(call)

# ======================
# 📥 إضافة كومبو
# ======================

@bot.callback_query_handler(func=lambda call: call.data == "admin_add_combo")
def admin_add_combo(call):
    if not is_admin(call.from_user.id):
        return
    user_states[call.from_user.id] = "waiting_combo_file"
    try:
        bot.edit_message_text("📤 أرسل ملف الكومبو TXT", call.message.chat.id, call.message.message_id)
    except:
        bot.send_message(call.message.chat.id, "📤 أرسل ملف الكومبو TXT")

@bot.message_handler(content_types=['document'], func=lambda msg: user_states.get(msg.from_user.id) == "waiting_combo_file" and is_admin(msg.from_user.id))
def handle_combo_file(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        content = downloaded_file.decode('utf-8')
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        if not lines:
            bot.reply_to(message, "❌ الملف فارغ")
            return
        first_num = clean_number(lines[0])
        country_code = None
        for code in COUNTRY_CODES:
            if first_num.startswith(code):
                country_code = code
                break
        if not country_code:
            bot.reply_to(message, "❌ لا يمكن تحديد الدولة")
            return
        save_combo(country_code, lines)
        name, flag, _ = COUNTRY_CODES[country_code]
        bot.reply_to(message, f"✅ تم حفظ الكومبو لـ {flag} {name}\nعدد الأرقام: {len(lines)}")
        del user_states[message.from_user.id]
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {e}")

# ======================
# 🗑️ حذف الكومبوهات
# ======================

@bot.callback_query_handler(func=lambda call: call.data == "admin_del_combo")
def admin_del_combo(call):
    if not is_admin(call.from_user.id):
        return
    combos = get_all_combos()
    if not combos:
        bot.answer_callback_query(call.id, "لا توجد كومبوهات")
        return
    markup = types.InlineKeyboardMarkup(row_width=2)
    for country_code, combo_index in combos:
        if country_code in COUNTRY_CODES:
            name, flag, _ = COUNTRY_CODES[country_code]
            markup.add(types.InlineKeyboardButton(f"{flag} {name}", callback_data=f"del_combo_{country_code}_{combo_index}", style='danger'))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel", style='primary'))
    try:
        bot.edit_message_text("اختر الكومبو للحذف:", call.message.chat.id, call.message.message_id, reply_markup=markup)
    except:
        bot.send_message(call.message.chat.id, "اختر الكومبو للحذف:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("del_combo_"))
def confirm_del_combo(call):
    if not is_admin(call.from_user.id):
        return
    parts = call.data.split("_")
    country_code = parts[2]
    combo_index = int(parts[3])
    delete_combo(country_code, combo_index)
    bot.answer_callback_query(call.id, "✅ تم الحذف")
    admin_del_combo(call)

# ======================
# 📨 إرسال الأكواد
# ======================

@bot.message_handler(commands=['sendotp'])
def send_otp_command(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ للمطورين فقط")
        return

    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, "الاستخدام: /sendotp <رقم> <كود>")
        return

    phone = args[1]
    otp = args[2]
    full_message = " ".join(args[3:]) if len(args) > 3 else f"Your code: {otp}"

    user_id = get_user_by_number(phone)
    clean_phone = clean_number(phone)
    log_otp(clean_phone, otp, full_message, user_id)

    if user_id:
        try:
            bot.send_message(user_id, f"📞 الرقم: {clean_phone}\n🔐 الكود: {otp}")
            bot.reply_to(message, f"✅ تم إرسال {otp} إلى المستخدم {user_id}")
        except:
            bot.reply_to(message, f"❌ فشل الإرسال")
    else:
        bot.reply_to(message, f"⚠️ لا يوجد مستخدم للرقم {phone}")

# ======================
# ▶️ تشغيل البوت
# ======================

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 تشغيل البوت المطور - النسخة المحسنة")
    print("=" * 50)
    print("المميزات الجديدة:")
    print("✓ نظام نسخ احتياطي تلقائي للمستخدمين")
    print("✓ استعادة البيانات عند حذف قاعدة البيانات")
    print("✓ تحسين سرعة الاستعلامات مع Caching")
    print("✓ إدارة آمنة للاتصالات مع locks")
    print("✓ أرقام مجانية ومدفوعة")
    print("✓ نظام نقاط ودعوات (رابط بالايدي)")
    print("✓ حذف الأرقام من الكومبو والملفات")
    print("✓ حفظ ايديات المستخدمين في ملف منفصل")
    print("✓ أزرار ملونة بأسلوب حديث")
    print("✓ نظام اشتراك اجباري متعدد القنوات")
    print("=" * 50)

    check_and_restore_db()

    while True:
        try:
            bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            print(f"خطأ في الاتصال: {e}")
            time.sleep(1)