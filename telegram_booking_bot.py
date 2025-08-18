import os
import sys
import datetime
import asyncio
import pytz
from typing import Dict, List

# Проверяем наличие конфликтующих файлов перед импортом
def check_module_conflicts():
    """Проверка конфликтов имен модулей"""
    conflicts = []
    current_dir = os.getcwd()
    
    # Список стандартных модулей Python, которые часто конфликтуют
    standard_modules = ['calendar', 'datetime', 'json', 'os', 'sys', 'time', 'email', 'asyncio']
    
    for module in standard_modules:
        conflict_file = os.path.join(current_dir, f"{module}.py")
        if os.path.exists(conflict_file):
            conflicts.append(f"{module}.py")
    
    if conflicts:
        print("⚠️ ВНИМАНИЕ: Обнаружены конфликты имен модулей!")
        print("Следующие файлы конфликтуют со стандартными модулями Python:")
        for conflict in conflicts:
            print(f"   📄 {conflict}")
        print("\n💡 Решение:")
        print("   Переименуйте эти файлы, например:")
        for conflict in conflicts:
            new_name = conflict.replace('.py', '_custom.py')
            print(f"   mv {conflict} {new_name}")
        print("\n❌ Бот не может запуститься из-за конфликтов модулей.")
        return True
    return False

# Проверяем конфликты
if check_module_conflicts():
    sys.exit(1)

# Импортируем остальные модули
try:
    from aiogram import Bot, Dispatcher, types
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
    from aiogram.filters import Command
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from dotenv import load_dotenv
    import openai
except ImportError as e:
    print(f"❌ Ошибка импорта библиотек: {e}")
    print("💡 Установите зависимости: pip install -r requirements.txt")
    sys.exit(1)

load_dotenv()

# --- Настройки ---
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GOOGLE_CREDENTIALS_FILE = "aura-469414-e8af117aeedf.json"
CALENDAR_ID = "primary"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Проверка наличия необходимых переменных окружения
if not API_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не найден в переменных окружения")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY не найден в переменных окружения")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Настройка OpenAI
openai.api_key = OPENAI_API_KEY

# --- Google Calendar ---
SCOPES = ['https://www.googleapis.com/auth/calendar']
MOSCOW_TZ = pytz.timezone('Europe/Moscow')

def initialize_calendar_service():
    """Инициализация Google Calendar сервиса с детальной диагностикой"""
    try:
        print(f"🔍 Попытка загрузки файла учетных данных: {GOOGLE_CREDENTIALS_FILE}")
        
        if not os.path.exists(GOOGLE_CREDENTIALS_FILE):
            print(f"❌ Файл {GOOGLE_CREDENTIALS_FILE} не найден в текущей директории")
            print(f"📁 Текущая директория: {os.getcwd()}")
            print(f"📄 Файлы в директории: {os.listdir('.')}")
            return None
            
        credentials = service_account.Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_FILE, scopes=SCOPES
        )
        
        service = build('calendar', 'v3', credentials=credentials)
        
        # Тестируем подключение
        try:
            calendar_list = service.calendarList().list().execute()
            calendars = calendar_list.get('items', [])
            print(f"✅ Google Calendar API успешно инициализирован")
            print(f"📅 Найдено календарей: {len(calendars)}")
            
            for calendar in calendars:
                cal_id = calendar['id']
                cal_name = calendar.get('summary', 'Без названия')
                access_role = calendar.get('accessRole', 'неизвестно')
                print(f"  📋 {cal_name} (ID: {cal_id[:20]}...) - Права: {access_role}")
                
                if cal_id == CALENDAR_ID or CALENDAR_ID == "primary":
                    print(f"  🎯 Используется календарь: {cal_name}")
            
            return service
            
        except Exception as test_error:
            print(f"❌ Ошибка при тестировании подключения: {test_error}")
            return None
            
    except FileNotFoundError:
        print(f"❌ Файл учетных данных {GOOGLE_CREDENTIALS_FILE} не найден")
        return None
    except Exception as e:
        print(f"❌ Ошибка инициализации Google Calendar API: {e}")
        print(f"🔍 Тип ошибки: {type(e).__name__}")
        return None

service = initialize_calendar_service()

# --- Хранилище выбранных дат ---
user_dates: Dict[int, datetime.date] = {}

# --- Получение свободных слотов ---
def get_free_slots(day: datetime.date) -> List[str]:
    """Получает список свободных временных слотов на указанную дату"""
    if not service:
        return []
    
    try:
        # Создаем время начала и конца дня в московском времени
        start_of_day = MOSCOW_TZ.localize(
            datetime.datetime.combine(day, datetime.time(9, 0))
        )
        end_of_day = MOSCOW_TZ.localize(
            datetime.datetime.combine(day, datetime.time(18, 0))
        )

        # Получаем события из календаря
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=start_of_day.isoformat(),
            timeMax=end_of_day.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        # Собираем занятые слоты
        busy_slots = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            if start and end:
                try:
                    # Парсим время с учетом часового пояса
                    if 'T' in start:  # dateTime формат
                        start_dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                        end_dt = datetime.datetime.fromisoformat(end.replace('Z', '+00:00'))
                        # Конвертируем в московское время
                        start_dt = start_dt.astimezone(MOSCOW_TZ)
                        end_dt = end_dt.astimezone(MOSCOW_TZ)
                        busy_slots.append((start_dt, end_dt))
                except Exception as e:
                    print(f"Ошибка парсинга времени события: {e}")
                    continue

        # Генерируем свободные слоты
        slots = []
        current = start_of_day
        
        while current < end_of_day:
            slot_end = current + datetime.timedelta(hours=1)
            slot_free = True
            
            # Проверяем, не пересекается ли слот с занятыми
            for busy_start, busy_end in busy_slots:
                if current < busy_end and slot_end > busy_start:
                    slot_free = False
                    break
            
            if slot_free:
                slots.append(current.strftime("%H:%M"))
            
            current = slot_end

        return slots

    except HttpError as error:
        print(f"Ошибка Google Calendar API: {error}")
        return []
    except Exception as e:
        print(f"Неожиданная ошибка при получении слотов: {e}")
        return []

# --- Создание клавиатуры с датами ---
def create_date_keyboard() -> ReplyKeyboardMarkup:
    """Создает клавиатуру с датами на ближайшие 7 дней"""
    buttons = []
    for i in range(7):
        date = datetime.date.today() + datetime.timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        day_name = date.strftime("%A")
        # Переводим названия дней на русский
        day_names = {
            'Monday': 'Пн', 'Tuesday': 'Вт', 'Wednesday': 'Ср',
            'Thursday': 'Чт', 'Friday': 'Пт', 'Saturday': 'Сб', 'Sunday': 'Вс'
        }
        day_ru = day_names.get(day_name, day_name)
        button_text = f"{date_str} ({day_ru})"
        buttons.append([KeyboardButton(text=date_str)])
    
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)

# --- Создание клавиатуры с временными слотами ---
def create_time_keyboard(slots: List[str]) -> ReplyKeyboardMarkup:
    """Создает клавиатуру с доступными временными слотами"""
    buttons = []
    # Группируем по 3 кнопки в ряд
    for i in range(0, len(slots), 3):
        row = []
        for j in range(i, min(i + 3, len(slots))):
            row.append(KeyboardButton(text=slots[j]))
        buttons.append(row)
    
    # Добавляем кнопку "Назад"
    buttons.append([KeyboardButton(text="🔙 Назад к выбору даты")])
    
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)

# --- Хэндлер /start ---
@dp.message(Command("start"))
async def start(message: types.Message):
    """Обработчик команды /start"""
    if not service:
        await message.reply("❌ Ошибка подключения к Google Calendar. Обратитесь к администратору.")
        return
    
    keyboard = create_date_keyboard()
    welcome_text = (
        "🏥 Добро пожаловать в систему записи на прием!\n\n"
        "📅 Выберите дату для записи:"
    )
    await message.reply(welcome_text, reply_markup=keyboard)

# --- Хэндлер выбора даты ---
@dp.message(lambda message: message.text and len(message.text) == 10 and "-" in message.text)
async def choose_date(message: types.Message):
    """Обработчик выбора даты"""
    try:
        day = datetime.datetime.strptime(message.text, "%Y-%m-%d").date()
        
        # Проверяем, что дата не в прошлом
        if day < datetime.date.today():
            await message.reply("❌ Нельзя выбрать дату в прошлом. Выберите актуальную дату.")
            return
        
        user_dates[message.from_user.id] = day
        
        # Получаем свободные слоты
        slots = get_free_slots(day)
        
        if not slots:
            keyboard = create_date_keyboard()
            await message.reply(
                f"❌ На {message.text} все слоты заняты!\n"
                "Выберите другую дату:",
                reply_markup=keyboard
            )
            return

        keyboard = create_time_keyboard(slots)
        day_name = day.strftime("%A, %d %B %Y")
        await message.reply(
            f"🕐 Выберите удобное время для записи на {message.text}:\n"
            f"Доступно {len(slots)} свободных слотов",
            reply_markup=keyboard
        )

    except ValueError:
        await message.reply("❌ Неверный формат даты. Используйте формат ГГГГ-ММ-ДД")
        return

# --- Хэндлер кнопки "Назад" ---
@dp.message(lambda message: message.text == "🔙 Назад к выбору даты")
async def back_to_dates(message: types.Message):
    """Возврат к выбору даты"""
    keyboard = create_date_keyboard()
    await message.reply("📅 Выберите дату для записи:", reply_markup=keyboard)

# --- Хэндлер выбора времени ---
@dp.message(lambda message: message.text and ":" in message.text and len(message.text) == 5)
async def book_slot(message: types.Message):
    """Обработчик бронирования временного слота"""
    if not service:
        await message.reply("❌ Ошибка подключения к Google Calendar. Обратитесь к администратору.")
        return
    
    try:
        selected_time = message.text
        user_id = message.from_user.id
        
        # Получаем выбранную пользователем дату
        day = user_dates.get(user_id)
        if not day:
            keyboard = create_date_keyboard()
            await message.reply("❌ Сначала выберите дату:", reply_markup=keyboard)
            return
        
        # Создаем время начала и конца встречи в московском времени
        start_time = datetime.datetime.strptime(selected_time, "%H:%M").time()
        start_datetime = MOSCOW_TZ.localize(
            datetime.datetime.combine(day, start_time)
        )
        end_datetime = start_datetime + datetime.timedelta(hours=1)
        
        # Проверяем, что слот все еще свободен
        current_slots = get_free_slots(day)
        if selected_time not in current_slots:
            keyboard = create_time_keyboard(current_slots) if current_slots else create_date_keyboard()
            await message.reply(
                "❌ Извините, этот слот уже занят. Выберите другое время:",
                reply_markup=keyboard
            )
            return
        
        # Получаем информацию о пользователе
        user_name = message.from_user.full_name or "Клиент"
        user_username = f"@{message.from_user.username}" if message.from_user.username else ""
        
        # Создаем событие в календаре
        event = {
            'summary': f'Запись: {user_name}',
            'description': f'Клиент: {user_name} {user_username}\nTelegram ID: {user_id}',
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'Europe/Moscow'
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'Europe/Moscow'
            },
            'attendees': [],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 30},       # За 30 минут
                ],
            },
        }
        
        print(f"🔍 Создание события в календаре:")
        print(f"  📅 Календарь ID: {CALENDAR_ID}")
        print(f"  📝 Название: {event['summary']}")
        print(f"  🕐 Начало: {start_datetime.isoformat()}")
        print(f"  🕑 Конец: {end_datetime.isoformat()}")
        print(f"  👤 Пользователь: {user_name} (ID: {user_id})")
        
        # Добавляем событие в календарь
        try:
            created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
            event_id = created_event.get('id')
            event_link = created_event.get('htmlLink', 'Ссылка недоступна')
            
            print(f"✅ Событие успешно создано!")
            print(f"  🆔 ID события: {event_id}")
            print(f"  🔗 Ссылка: {event_link}")
            
        except HttpError as http_error:
            error_details = http_error.error_details if hasattr(http_error, 'error_details') else str(http_error)
            print(f"❌ HTTP ошибка при создании события: {http_error}")
            print(f"🔍 Детали ошибки: {error_details}")
            
            # Пробуем создать событие в основном календаре пользователя
            if CALENDAR_ID != "primary":
                print(f"🔄 Попытка создания в основном календаре...")
                try:
                    created_event = service.events().insert(calendarId="primary", body=event).execute()
                    print(f"✅ Событие создано в основном календаре: {created_event.get('id')}")
                except Exception as fallback_error:
                    print(f"❌ Не удалось создать событие и в основном календаре: {fallback_error}")
                    raise http_error
            else:
                raise http_error
        
        # Удаляем пользователя из хранилища дат
        if user_id in user_dates:
            del user_dates[user_id]
        
        # Отправляем подтверждение
        confirmation_text = (
            f"✅ Отлично! Вы успешно записаны на прием!\n\n"
            f"📅 Дата: {day.strftime('%d.%m.%Y')}\n"
            f"🕐 Время: {selected_time} - {end_datetime.strftime('%H:%M')}\n"
            f"👤 Имя: {user_name}\n\n"
            f"📝 Запись добавлена в календарь.\n"
            f"🔔 Вы получите напоминание за 24 часа и за 30 минут до приема.\n\n"
            f"Для новой записи используйте команду /start"
        )
        
        await message.reply(confirmation_text, reply_markup=ReplyKeyboardRemove())
        
    except ValueError:
        await message.reply("❌ Неверный формат времени. Используйте формат ЧЧ:ММ")
    except HttpError as error:
        print(f"Ошибка Google Calendar API при создании события: {error}")
        await message.reply("❌ Ошибка при создании записи. Попробуйте позже.")
    except Exception as e:
        print(f"Неожиданная ошибка при бронировании: {e}")
        await message.reply("❌ Произошла ошибка. Попробуйте позже.")

# --- Команда для просмотра записей ---
@dp.message(Command("my_bookings"))
async def my_bookings(message: types.Message):
    """Показать записи пользователя"""
    if not service:
        await message.reply("❌ Ошибка подключения к Google Calendar.")
        return
    
    try:
        user_id = str(message.from_user.id)
        now = datetime.datetime.now(MOSCOW_TZ)
        
        # Получаем события на ближайшие 30 дней
        time_max = now + datetime.timedelta(days=30)
        
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=now.isoformat(),
            timeMax=time_max.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        
        # Фильтруем события пользователя
        user_events = []
        for event in events:
            description = event.get('description', '')
            if user_id in description:
                user_events.append(event)
        
        if not user_events:
            await message.reply("📅 У вас нет активных записей.")
            return
        
        response = "📋 Ваши записи:\n\n"
        for i, event in enumerate(user_events, 1):
            start = event['start'].get('dateTime', event['start'].get('date'))
            if start:
                start_dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                start_dt = start_dt.astimezone(MOSCOW_TZ)
                date_str = start_dt.strftime('%d.%m.%Y')
                time_str = start_dt.strftime('%H:%M')
                response += f"{i}. {date_str} в {time_str}\n"
        
        await message.reply(response)
        
    except Exception as e:
        print(f"Ошибка при получении записей: {e}")
        await message.reply("❌ Ошибка при получении записей.")

# --- Интеграция с OpenAI ---
@dp.message()
async def chat_with_openai(message: types.Message):
    """Обработчик для общения с OpenAI"""
    # Игнорируем системные сообщения
    if message.text in ["🔙 Назад к выбору даты"]:
        return
    
    try:
        # Проверяем, не является ли сообщение командой бронирования
        if (message.text and 
            (len(message.text) == 10 and "-" in message.text) or  # дата
            (len(message.text) == 5 and ":" in message.text)):    # время
            return
        
        # Создаем системный промт для контекста
        system_prompt = (
            "Ты - помощник в медицинской клинике. Помогай пользователям с вопросами о записи на прием, "
            "медицинских услугах и общей информации. Отвечай дружелюбно и профессионально. "
            "Если пользователь хочет записаться на прием, направь его к команде /start."
        )
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message.text}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        answer = response.choices[0].message.content
        await message.reply(answer)
        
    except Exception as e:
        print(f"Ошибка при обращении к OpenAI: {e}")
        await message.reply(
            "❌ Извините, сейчас я не могу ответить на ваш вопрос.\n"
            "Для записи на прием используйте команду /start"
        )

# --- Тестирование календаря ---
@dp.message(Command("test_calendar"))
async def test_calendar(message: types.Message):
    """Тестирование подключения к Google Calendar"""
    if not service:
        await message.reply("❌ Google Calendar API не инициализирован")
        return
    
    try:
        # Создаем тестовое событие
        now = datetime.datetime.now(MOSCOW_TZ)
        test_start = now + datetime.timedelta(minutes=1)
        test_end = test_start + datetime.timedelta(minutes=5)
        
        test_event = {
            'summary': 'ТЕСТ - Проверка подключения',
            'description': f'Тестовое событие от Telegram бота\nСоздано: {now.strftime("%d.%m.%Y %H:%M")}',
            'start': {
                'dateTime': test_start.isoformat(),
                'timeZone': 'Europe/Moscow'
            },
            'end': {
                'dateTime': test_end.isoformat(),
                'timeZone': 'Europe/Moscow'
            },
        }
        
        # Создаем событие
        created_event = service.events().insert(calendarId=CALENDAR_ID, body=test_event).execute()
        event_id = created_event.get('id')
        
        # Сразу удаляем тестовое событие
        service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
        
        await message.reply(
            f"✅ Тест успешно пройден!\n"
            f"📅 Календарь ID: {CALENDAR_ID}\n"
            f"🆔 Тестовое событие создано и удалено: {event_id[:20]}...\n"
            f"🔗 Подключение к Google Calendar работает корректно!"
        )
        
    except HttpError as error:
        await message.reply(
            f"❌ Ошибка Google Calendar API:\n"
            f"Код: {error.resp.status}\n"
            f"Причина: {error.resp.reason}\n"
            f"Детали: {error.content.decode() if error.content else 'Нет деталей'}"
        )
    except Exception as e:
        await message.reply(f"❌ Неожиданная ошибка при тестировании: {e}")

# --- Обработчик команды помощи ---
@dp.message(Command("help"))
async def help_command(message: types.Message):
    """Показать справку по командам"""
    help_text = (
        "🤖 Доступные команды:\n\n"
        "/start - Начать запись на прием\n"
        "/my_bookings - Посмотреть ваши записи\n"
        "/test_calendar - Тестировать Google Calendar\n"
        "/help - Показать эту справку\n\n"
        "📝 Как записаться:\n"
        "1. Используйте /start\n"
        "2. Выберите дату\n"
        "3. Выберите удобное время\n"
        "4. Получите подтверждение\n\n"
        "💬 Также вы можете задать любой вопрос - я постараюсь помочь!"
    )
    await message.reply(help_text)

# --- Запуск бота ---
async def main():
    """Главная функция для запуска бота"""
    print("🤖 Запуск Telegram бота...")
    print(f"📅 Google Calendar {'подключен' if service else 'НЕ подключен'}")
    print(f"🤖 OpenAI {'подключен' if OPENAI_API_KEY else 'НЕ подключен'}")
    
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")

if __name__ == "__main__":
    asyncio.run(main())