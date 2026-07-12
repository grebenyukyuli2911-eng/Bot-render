import asyncio
import os
import threading
from datetime import datetime, date, timedelta
from flask import Flask

from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.executor import start_polling

# ─── Keep-alive сервер для Render ───────────────────────────────
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Бот работает!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# ─── Bot setup ────────────────────────────────────────────────────
TOKEN = "8635374750:AAHVDTtI7A_Z2Z4ls3dDU5vF5EgiSRKlRXo"

bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# ─── In-memory storage ───────────────────────────────────────────
users_db = {}

def get_user(user_id):
    if user_id not in users_db:
        users_db[user_id] = {
            "first_seen": date.today().isoformat(),
            "visits": 1
        }
    else:
        users_db[user_id]["visits"] += 1
    return users_db[user_id]

def user_count():
    return len(users_db)

# ─── Keyboards ────────────────────────────────────────────────────
def main_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("📅 Калькулятор срока", callback_data="calc_menu"),
        InlineKeyboardButton("📋 Права осуждённых", callback_data="rights"),
        InlineKeyboardButton("📝 Шаблоны документов", callback_data="templates"),
        InlineKeyboardButton("📞 Полезные контакты", callback_data="contacts"),
        InlineKeyboardButton("❓ Частые вопросы", callback_data="faq")
    )
    return keyboard

def calc_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("🔢 Расчёт УДО", callback_data="calc_udo"),
        InlineKeyboardButton("🔢 Замена наказания", callback_data="calc_replace"),
        InlineKeyboardButton("🔢 Срок обжалования", callback_data="calc_appeal"),
        InlineKeyboardButton("⬅️ Назад", callback_data="main")
    )
    return keyboard

def back_button():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("⬅️ Назад в меню", callback_data="main")
    )
    return keyboard

# ─── Handlers ─────────────────────────────────────────────────────
@dp.message_handler(commands=["start"])
async def cmd_start(message: Message):
    user = get_user(message.from_user.id)
    total_users = user_count()
    await message.answer(
        f"👋 <b>Добро пожаловать!</b>\n\n"
        f"Бот для осуждённых к принудительным работам и их родственников.\n\n"
        f"📊 Всего пользователей: <b>{total_users}</b>\n"
        f"⚠️ Информация справочная. Для точных консультаций обращайтесь к адвокату.",
        reply_markup=main_menu()
    )

@dp.callback_query_handler(lambda c: c.data == "main")
async def back_to_main(callback: CallbackQuery):
    total_users = user_count()
    await callback.message.edit_text(
        f"👋 Главное меню\n\n"
        f"📊 Всего пользователей: <b>{total_users}</b>\n\n"
        f"Выберите раздел:",
        reply_markup=main_menu()
    )
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "calc_menu")
async def show_calc_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "📅 <b>Калькулятор срока</b>\n\nВыберите тип расчёта:",
        reply_markup=calc_menu()
    )
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "calc_udo")
async def calc_udo(callback: CallbackQuery):
    text = (
        "🔢 <b>Расчёт УДО</b>\n\n"
        "📌 <b>Правило:</b>\n"
        "• Не менее 1/2 срока — преступления небольшой/средней тяжести\n"
        "• Не менее 2/3 срока — тяжкие преступления\n"
        "• Не менее 3/4 срока — особо тяжкие преступления\n\n"
        "📌 УДО возможно при положительной характеристике, возмещении ущерба и исправлении.\n\n"
        "✍️ <b>Пример:</b> Срок 2 года (24 мес), средняя тяжесть\n"
        "Минимум: 24 × 1/2 = <b>12 месяцев</b>"
    )
    await callback.message.edit_text(text, reply_markup=back_button())
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "calc_replace")
async def calc_replace(callback: CallbackQuery):
    text = (
        "🔢 <b>Замена неотбытой части наказания</b>\n\n"
        "📌 <b>Ст. 80 УК РФ:</b>\n"
        "Неотбитая часть принудительных работ может быть заменена лишением свободы или более мягким видом наказания.\n\n"
        "📌 <b>Условия:</b>\n"
        "• Отбыл не менее 1/3 срока\n"
        "• Положительная характеристика\n"
        "• Исправление подтверждено\n\n"
        "⚠️ Решение принимает суд."
    )
    await callback.message.edit_text(text, reply_markup=back_button())
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "calc_appeal")
async def calc_appeal(callback: CallbackQuery):
    text = (
        "🔢 <b>Сроки обжалования</b>\n\n"
        "📌 <b>Апелляция:</b> 10 суток со дня оглашения приговора\n"
        "📌 <b>Кассация:</b> 6 месяцев со дня вступления в силу\n"
        "📌 <b>Надзорная жалоба:</b> 3 месяца со дня вступления в силу\n\n"
        "⚠️ Пропущенные сроки восстанавливаются судом по ходатайству."
    )
    await callback.message.edit_text(text, reply_markup=back_button())
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "rights")
async def show_rights(callback: CallbackQuery):
    text = (
        "📋 <b>Права осуждённых к принудительным работам</b>\n\n"
        "1️⃣ <b>Трудовые:</b> оплата не ниже МРОТ, отчисления в ПФР, отпуск 18 дней/год\n\n"
        "2️⃣ <b>Социальные:</b> бесплатная медпомощь, свидания (до 4 ч), звонки (2 раза/мес)\n\n"
        "3️⃣ <b>Юридические:</b> адвокат без ограничений, обжалование, жалобы в прокуратуру/суд/ОНК\n\n"
        "4️⃣ <b>Религиозные:</b> исповедание религии, встреча со священнослужителем\n\n"
        "⚠️ За нарушением прав обращайтесь к начальнику учреждения, в прокуратуру, суд или ОНК."
    )
    await callback.message.edit_text(text, reply_markup=back_button())
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "templates")
async def show_templates(callback: CallbackQuery):
    text = (
        "📝 <b>Шаблоны документов</b>\n\n"
        "📌 <b>1. Ходатайство о свидании</b>\n\n"
        "<code>В начальнику ИЦ-___\n"
        "от осуждённого Иванова И.И.\n"
        "Дата рождения: ___.___._____\n"
        "Статья: ___ ч. ___\n"
        "Срок: ___\n\n"
        "ХОДАТАЙСТВО\n\n"
        "Прошу разрешить свидание с ___ (ФИО, родство)\n"
        "___ числа ___ месяца ___ года.\n\n"
        "Основание: ст. 88 Закона об исполнении наказаний.\n\n"
        "Дата: ___.___._____\n"
        "Подпись: ___________</code>\n\n"
        "📌 <b>2. Жалоба на действия администрации</b>\n\n"
        "<code>В прокуратуру ___________ района/города\n"
        "от осуждённого ___________\n\n"
        "ЖАЛОБА\n\n"
        "Я, ___________, осуждённый к принудительным работам,\n"
        "сроком на ___ по ст. ___ УК РФ, отбываю наказание в ИЦ-___.\n\n"
        "___ (описание нарушения прав)\n\n"
        "На основании изложенного, руководствуясь ст. 254, 255 УПК РФ,\n"
        "прошу провести проверку и принять меры.\n\n"
        "Приложения: ___\n\n"
        "Дата: ___.___._____\n"
        "Подпись: ___________</code>\n\n"
        "📌 <b>3. Заявление на УДО</b>\n\n"
        "<code>В ___ районный суд\n"
        "г. ___________\n\n"
        "ЗАЯВЛЕНИЕ\n"
        "о применении условно-досрочного освобождения\n\n"
        "Я, ___________, осуждён(а) по приговору ___ суда от ___.___._____\n"
        "по ст. ___ ч. ___ УК РФ к ___.\n\n"
        "Фактически отбыл(а) ___ из ___.\n\n"
        "Имею положительную характеристику.\n"
        "Возмещён ущерб (если применимо).\n\n"
        "Прошу применить УДО.\n\n"
        "Приложения:\n"
        "1. Копия приговора\n"
        "2. Справка об отбытых сроках\n"
        "3. Характеристика\n"
        "4. Документы о возмещении ущерба\n\n"
        "Дата: ___.___._____\n"
        "Подпись: ___________</code>"
    )
    await callback.message.edit_text(text, reply_markup=back_button())
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "contacts")
async def show_contacts(callback: CallbackQuery):
    text = (
        "📞 <b>Полезные контакты</b>\n\n"
        "📌 <b>ФСИН России</b>\n"
        "• fsin.gov.ru\n"
        "• 8 (495) 987-17-77\n\n"
        "📌 <b>Бесплатные юрконсультации</b>\n"
        "• ФПА РФ: 8 (800) 200-20-20\n"
        "• Минюст: 8 (800) 200-22-03\n\n"
        "📌 <b>Правозащита</b>\n"
        "• zonaprava.org\n"
        "• apologia.ru\n\n"
        "📌 <b>ОНК</b>\n"
        "• onk.fsin.gov.ru\n"
        "• oprf.ru"
    )
    await callback.message.edit_text(text, reply_markup=back_button())
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "faq")
async def show_faq(callback: CallbackQuery):
    text = (
        "❓ <b>Частые вопросы</b>\n\n"
        "❓ <b>Сколько рабочий день?</b>\n"
        "📌 Не более 8 часов, перерыв не менее 1 часа.\n\n"
        "❓ <b>Можно ли перевести в другой регион?</b>\n"
        "📌 Да, по ходатайству администрации или родственников.\n\n"
        "❓ <b>Что можно передавать?</b>\n"
        "📌 Одежда, обувь, бельё, продукты (до 20 кг/мес), книги, лекарства по рецепту.\n\n"
        "❓ <b>Как часто звонить?</b>\n"
        "📌 До 2 раз в месяц по 15 минут.\n\n"
        "❓ <b>Как получить УДО?</b>\n"
        "📌 Отбыть минимум половину срока, положительная характеристика, возмещение ущерба."
    )
    await callback.message.edit_text(text, reply_markup=back_button())
    await callback.answer()

# ─── Main ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Запускаем Flask в отдельном потоке (для keep-alive)
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Запускаем бота
    print("🤖 Бот запущен!")
    start_polling(dp, skip_updates=True)
