import os
import json
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

# ============================
# CONFIG
# ============================
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "123456789").split(",")]  # Your Telegram user ID
DATA_FILE = "data.json"

# ============================
# DATA MANAGEMENT
# ============================
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "categories": {
            "🍺 သောက်ဆိုင်/Bar": [],
            "💆 Massage": [],
            "🎮 Entertainment": [],
            "🏨 Hotel": [],
            "🍜 စားသောက်ဆိုင်": []
        }
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Sample data for demo
def init_sample_data():
    if not os.path.exists(DATA_FILE):
        data = {
            "categories": {
                "🍺 သောက်ဆိုင်/Bar": [
                    {"name": "XO Bar", "address": "ရန်ကုန်မြို့လယ်", "phone": "09-111111", "note": ""},
                    {"name": "Sky Bar", "address": "Sule Area", "phone": "09-222222", "note": "Rooftop view"}
                ],
                "💆 Massage": [
                    {"name": "တိဘက် Massage", "address": "မင်္ဂလာဒုံ", "phone": "09-333333", "note": "24hr"},
                    {"name": "Lotus Spa", "address": "ဗဟန်း", "phone": "09-444444", "note": "VIP Room ရှိ"}
                ],
                "🎮 Entertainment": [
                    {"name": "Frequency Club", "address": "Downtown", "phone": "09-555555", "note": "Friday Special"},
                ],
                "🏨 Hotel": [
                    {"name": "Central Hotel", "address": "မြို့လယ်", "phone": "09-666666", "note": ""},
                ],
                "🍜 စားသောက်ဆိုင်": [
                    {"name": "မြန်မာ့အရသာ", "address": "ဒဂုံ", "phone": "09-777777", "note": "24hr open"},
                ]
            }
        }
        save_data(data)

# ============================
# KEYBOARDS
# ============================
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📋 Category ကြည့်မည်", callback_data="show_categories")],
        [InlineKeyboardButton("🎲 Random တစ်ခု ကြည့်မည်", callback_data="random_place")],
        [InlineKeyboardButton("🔍 Search လုပ်မည်", callback_data="search_mode")],
    ]
    return InlineKeyboardMarkup(keyboard)

def categories_keyboard(data):
    keyboard = []
    for cat in data["categories"].keys():
        count = len(data["categories"][cat])
        keyboard.append([InlineKeyboardButton(f"{cat} ({count})", callback_data=f"cat_{cat}")])
    keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)

def places_keyboard(places, cat_name):
    keyboard = []
    for i, place in enumerate(places):
        keyboard.append([InlineKeyboardButton(f"📍 {place['name']}", callback_data=f"place_{cat_name}_{i}")])
    keyboard.append([InlineKeyboardButton("⬅️ နောက်သို့", callback_data="show_categories")])
    keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)

# ============================
# HANDLERS
# ============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    init_sample_data()
    user = update.effective_user
    text = (
        f"👋 မင်္ဂလာပါ {user.first_name}!\n\n"
        "🗺️ *Venue Directory Bot* မှ ကြိုဆိုပါသည်\n\n"
        "ဘာ ရှာဖွေလိုပါသလဲ?"
    )
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = load_data()
    cb = query.data

    # Main Menu
    if cb == "main_menu":
        await query.edit_message_text(
            "🏠 *Main Menu*\n\nဘာ ရှာဖွေလိုပါသလဲ?",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )

    # Show Categories
    elif cb == "show_categories":
        await query.edit_message_text(
            "📋 *Categories*\n\nCategory တစ်ခု ရွေးချယ်ပါ:",
            parse_mode="Markdown",
            reply_markup=categories_keyboard(data)
        )

    # Category selected
    elif cb.startswith("cat_"):
        cat_name = cb[4:]
        places = data["categories"].get(cat_name, [])
        if not places:
            await query.edit_message_text(
                f"{cat_name}\n\n❌ မည်သည့် Venue မျှ မရှိသေးပါ။",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("⬅️ နောက်သို့", callback_data="show_categories")
                ]])
            )
        else:
            await query.edit_message_text(
                f"{cat_name}\n\n📍 Venue {len(places)} ခု ရှိသည်:",
                reply_markup=places_keyboard(places, cat_name)
            )

    # Place detail
    elif cb.startswith("place_"):
        parts = cb.split("_", 2)
        cat_name = parts[1]
        idx = int(parts[2])
        places = data["categories"].get(cat_name, [])
        if idx < len(places):
            p = places[idx]
            text = (
                f"📍 *{p['name']}*\n"
                f"🏷️ Category: {cat_name}\n"
                f"📮 Address: {p.get('address', 'N/A')}\n"
                f"📞 Phone: {p.get('phone', 'N/A')}\n"
            )
            if p.get("note"):
                text += f"📝 Note: {p['note']}\n"
            await query.edit_message_text(
                text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(f"⬅️ {cat_name} သို့ ပြန်သွားမည်", callback_data=f"cat_{cat_name}")],
                    [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
                ])
            )

    # Random
    elif cb == "random_place":
        all_places = []
        for cat, places in data["categories"].items():
            for p in places:
                all_places.append((cat, p))
        if not all_places:
            await query.edit_message_text("❌ Venue မရှိသေးပါ။", reply_markup=main_menu_keyboard())
        else:
            cat, p = random.choice(all_places)
            text = (
                f"🎲 *Random Pick!*\n\n"
                f"📍 *{p['name']}*\n"
                f"🏷️ Category: {cat}\n"
                f"📮 Address: {p.get('address', 'N/A')}\n"
                f"📞 Phone: {p.get('phone', 'N/A')}\n"
            )
            if p.get("note"):
                text += f"📝 Note: {p['note']}\n"
            await query.edit_message_text(
                text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🎲 တစ်ခု ထပ်ကြည့်မည်", callback_data="random_place")],
                    [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
                ])
            )

    # Search mode
    elif cb == "search_mode":
        context.user_data["searching"] = True
        await query.edit_message_text(
            "🔍 *Search Mode*\n\nရှာလိုသော နာမည် သို့မဟုတ် နေရာ ရိုက်ထည့်ပါ:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ Cancel", callback_data="main_menu")
            ]])
        )

# Search handler
async def search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("searching"):
        await update.message.reply_text(
            "⬇️ Menu မှ ရွေးချယ်ပါ:",
            reply_markup=main_menu_keyboard()
        )
        return

    context.user_data["searching"] = False
    query_text = update.message.text.lower()
    data = load_data()
    results = []

    for cat, places in data["categories"].items():
        for p in places:
            if (query_text in p["name"].lower() or
                query_text in p.get("address", "").lower() or
                query_text in p.get("note", "").lower()):
                results.append((cat, p))

    if not results:
        await update.message.reply_text(
            f"❌ *'{update.message.text}'* နှင့် ကိုက်ညီသည့် Venue မတွေ့ပါ။",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
    else:
        text = f"🔍 *'{update.message.text}'* - {len(results)} ခု တွေ့ရှိ:\n\n"
        for cat, p in results[:10]:  # Max 10 results
            text += f"📍 *{p['name']}* ({cat})\n"
            text += f"   📞 {p.get('phone', 'N/A')}\n\n"
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())

# ============================
# ADMIN COMMANDS
# ============================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Admin သာ ဝင်ရောက်နိုင်သည်။")
        return

    text = (
        "⚙️ *Admin Panel*\n\n"
        "Commands:\n"
        "`/add <category> | <name> | <address> | <phone> | <note>`\n"
        "`/remove <category> | <name>`\n"
        "`/list` - Venue အားလုံး ကြည့်မည်\n\n"
        "Category များ:\n"
        "• 🍺 သောက်ဆိုင်/Bar\n"
        "• 💆 Massage\n"
        "• 🎮 Entertainment\n"
        "• 🏨 Hotel\n"
        "• 🍜 စားသောက်ဆိုင်"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def add_venue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Admin သာ ဝင်ရောက်နိုင်သည်။")
        return

    try:
        args_text = " ".join(context.args)
        parts = [p.strip() for p in args_text.split("|")]
        cat = parts[0]
        name = parts[1]
        address = parts[2] if len(parts) > 2 else ""
        phone = parts[3] if len(parts) > 3 else ""
        note = parts[4] if len(parts) > 4 else ""

        data = load_data()
        if cat not in data["categories"]:
            data["categories"][cat] = []

        data["categories"][cat].append({
            "name": name, "address": address, "phone": phone, "note": note
        })
        save_data(data)
        await update.message.reply_text(f"✅ *{name}* ကို *{cat}* တွင် ထည့်သွင်းပြီးပါပြီ။", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(
            "❌ Format မှားနေသည်။\n"
            "Example: `/add 🍺 သောက်ဆိုင်/Bar | My Bar | ဗဟန်း | 09-123456 | VIP Room`",
            parse_mode="Markdown"
        )

async def remove_venue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Admin သာ ဝင်ရောက်နိုင်သည်။")
        return

    try:
        args_text = " ".join(context.args)
        parts = [p.strip() for p in args_text.split("|")]
        cat = parts[0]
        name = parts[1]

        data = load_data()
        original = data["categories"].get(cat, [])
        data["categories"][cat] = [p for p in original if p["name"] != name]
        removed = len(original) - len(data["categories"][cat])
        save_data(data)

        if removed:
            await update.message.reply_text(f"✅ *{name}* ကို ဖျက်ပြီးပါပြီ။", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"❌ *{name}* မတွေ့ပါ။", parse_mode="Markdown")
    except:
        await update.message.reply_text("❌ Format: `/remove Category | Name`", parse_mode="Markdown")

async def list_venues(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        return
    data = load_data()
    text = "📋 *Venue List (Admin)*\n\n"
    for cat, places in data["categories"].items():
        text += f"*{cat}* ({len(places)} ခု)\n"
        for p in places:
            text += f"  • {p['name']} - {p.get('phone','')}\n"
        text += "\n"
    await update.message.reply_text(text, parse_mode="Markdown")

# ============================
# MAIN
# ============================
def main():
    init_sample_data()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("add", add_venue))
    app.add_handler(CommandHandler("remove", remove_venue))
    app.add_handler(CommandHandler("list", list_venues))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_handler))

    print("🤖 Bot started!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
