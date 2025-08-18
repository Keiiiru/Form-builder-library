#!/usr/bin/env python3
"""
Скрипт для диагностики проблем с Google Calendar API
Запустите этот скрипт для проверки подключения и прав доступа
"""

import os
import sys
import datetime
import pytz

# Проверяем наличие конфликтующих файлов
def check_module_conflicts():
    """Проверка конфликтов имен модулей"""
    conflicts = []
    current_dir = os.getcwd()
    
    # Список стандартных модулей Python, которые часто конфликтуют
    standard_modules = ['calendar', 'datetime', 'json', 'os', 'sys', 'time', 'email']
    
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
        print()
        return conflicts
    return []

# Проверяем конфликты перед импортом
conflicts = check_module_conflicts()
if conflicts:
    print("❌ Невозможно продолжить из-за конфликтов модулей.")
    print("Переименуйте указанные файлы и запустите скрипт снова.")
    sys.exit(1)

# Теперь безопасно импортируем модули Google API
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError as e:
    print(f"❌ Ошибка импорта Google API библиотек: {e}")
    print("💡 Установите зависимости: pip install -r requirements.txt")
    sys.exit(1)

# Настройки
GOOGLE_CREDENTIALS_FILE = "aura-469414-e8af117aeedf.json"
CALENDAR_ID = "primary"
SCOPES = ['https://www.googleapis.com/auth/calendar']
MOSCOW_TZ = pytz.timezone('Europe/Moscow')

def main():
    print("🔍 Диагностика Google Calendar API")
    print("=" * 50)
    
    # 1. Проверяем наличие файла с учетными данными
    print(f"\n1️⃣ Проверка файла учетных данных:")
    print(f"   📁 Текущая директория: {os.getcwd()}")
    print(f"   📄 Ищем файл: {GOOGLE_CREDENTIALS_FILE}")
    
    if not os.path.exists(GOOGLE_CREDENTIALS_FILE):
        print(f"   ❌ Файл {GOOGLE_CREDENTIALS_FILE} не найден!")
        print(f"   📋 Файлы в директории:")
        for file in os.listdir('.'):
            if file.endswith('.json'):
                print(f"      📄 {file}")
        print("\n💡 Решение:")
        print("   - Убедитесь, что JSON файл с учетными данными находится в той же папке")
        print("   - Проверьте правильность имени файла")
        return False
    else:
        print(f"   ✅ Файл найден: {GOOGLE_CREDENTIALS_FILE}")
    
    # 2. Проверяем загрузку учетных данных
    print(f"\n2️⃣ Загрузка учетных данных:")
    try:
        credentials = service_account.Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_FILE, scopes=SCOPES
        )
        print("   ✅ Учетные данные успешно загружены")
        
        # Показываем информацию о сервисном аккаунте
        with open(GOOGLE_CREDENTIALS_FILE, 'r') as f:
            import json
            cred_data = json.load(f)
            service_email = cred_data.get('client_email', 'Неизвестно')
            project_id = cred_data.get('project_id', 'Неизвестно')
            print(f"   📧 Email сервисного аккаунта: {service_email}")
            print(f"   🏗️ ID проекта: {project_id}")
            
    except Exception as e:
        print(f"   ❌ Ошибка загрузки учетных данных: {e}")
        print("\n💡 Решение:")
        print("   - Проверьте корректность JSON файла")
        print("   - Убедитесь, что файл не поврежден")
        return False
    
    # 3. Создаем сервис Google Calendar
    print(f"\n3️⃣ Инициализация Google Calendar API:")
    try:
        service = build('calendar', 'v3', credentials=credentials)
        print("   ✅ API сервис создан успешно")
    except Exception as e:
        print(f"   ❌ Ошибка создания API сервиса: {e}")
        return False
    
    # 4. Получаем список календарей
    print(f"\n4️⃣ Получение списка календарей:")
    try:
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])
        
        if not calendars:
            print("   ❌ Календари не найдены!")
            print("\n💡 Возможные причины:")
            print("   - У сервисного аккаунта нет доступа ни к одному календарю")
            print("   - Необходимо предоставить доступ к календарю")
            return False
        
        print(f"   ✅ Найдено календарей: {len(calendars)}")
        print("\n   📅 Доступные календари:")
        
        target_calendar = None
        for i, calendar in enumerate(calendars, 1):
            cal_id = calendar['id']
            cal_name = calendar.get('summary', 'Без названия')
            access_role = calendar.get('accessRole', 'неизвестно')
            is_primary = calendar.get('primary', False)
            
            print(f"   {i}. {cal_name}")
            print(f"      🆔 ID: {cal_id}")
            print(f"      🔐 Права доступа: {access_role}")
            print(f"      ⭐ Primary: {'Да' if is_primary else 'Нет'}")
            
            if cal_id == CALENDAR_ID or (CALENDAR_ID == "primary" and is_primary):
                target_calendar = calendar
                print(f"      🎯 ИСПОЛЬЗУЕТСЯ БОТОМ")
            print()
        
        if not target_calendar:
            print(f"   ⚠️ Целевой календарь '{CALENDAR_ID}' не найден!")
            print("\n💡 Решение:")
            print("   - Измените CALENDAR_ID в коде на один из доступных")
            print("   - Или предоставьте доступ к нужному календарю")
            return False
            
    except HttpError as error:
        print(f"   ❌ HTTP ошибка при получении календарей: {error}")
        print(f"   📄 Детали: {error.content.decode() if error.content else 'Нет деталей'}")
        return False
    except Exception as e:
        print(f"   ❌ Неожиданная ошибка: {e}")
        return False
    
    # 5. Тестируем создание события
    print(f"5️⃣ Тестирование создания события:")
    try:
        now = datetime.datetime.now(MOSCOW_TZ)
        test_start = now + datetime.timedelta(minutes=1)
        test_end = test_start + datetime.timedelta(minutes=5)
        
        test_event = {
            'summary': 'ТЕСТ - Диагностика API',
            'description': f'Тестовое событие для проверки API\nСоздано: {now.strftime("%d.%m.%Y %H:%M:%S")}',
            'start': {
                'dateTime': test_start.isoformat(),
                'timeZone': 'Europe/Moscow'
            },
            'end': {
                'dateTime': test_end.isoformat(),
                'timeZone': 'Europe/Moscow'
            },
        }
        
        print(f"   📝 Создание тестового события...")
        print(f"   🕐 Время: {test_start.strftime('%d.%m.%Y %H:%M')} - {test_end.strftime('%H:%M')}")
        
        created_event = service.events().insert(calendarId=CALENDAR_ID, body=test_event).execute()
        event_id = created_event.get('id')
        event_link = created_event.get('htmlLink', '')
        
        print(f"   ✅ Событие успешно создано!")
        print(f"   🆔 ID события: {event_id}")
        print(f"   🔗 Ссылка: {event_link}")
        
        # Удаляем тестовое событие
        print(f"   🗑️ Удаление тестового события...")
        service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
        print(f"   ✅ Тестовое событие удалено")
        
    except HttpError as error:
        print(f"   ❌ HTTP ошибка при создании события: {error}")
        print(f"   📄 Код ошибки: {error.resp.status}")
        print(f"   📄 Причина: {error.resp.reason}")
        print(f"   📄 Детали: {error.content.decode() if error.content else 'Нет деталей'}")
        
        if error.resp.status == 403:
            print("\n💡 Ошибка 403 - Недостаточно прав:")
            print("   - Убедитесь, что сервисный аккаунт имеет права на редактирование календаря")
            print("   - Добавьте email сервисного аккаунта в настройки календаря с правами редактирования")
        elif error.resp.status == 404:
            print("\n💡 Ошибка 404 - Календарь не найден:")
            print("   - Проверьте правильность CALENDAR_ID")
            print("   - Убедитесь, что календарь существует и доступен")
            
        return False
    except Exception as e:
        print(f"   ❌ Неожиданная ошибка: {e}")
        return False
    
    # 6. Финальная проверка
    print(f"\n🎉 Все тесты пройдены успешно!")
    print("✅ Google Calendar API работает корректно")
    print("✅ Права доступа настроены правильно")
    print("✅ Бот может создавать события в календаре")
    
    print(f"\n📋 Конфигурация:")
    print(f"   📄 Файл учетных данных: {GOOGLE_CREDENTIALS_FILE}")
    print(f"   📅 Календарь ID: {CALENDAR_ID}")
    print(f"   📧 Сервисный аккаунт: {service_email}")
    print(f"   🏗️ Проект: {project_id}")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Диагностика выявила проблемы!")
        print("Исправьте указанные проблемы и запустите тест снова.")
        exit(1)
    else:
        print("\n✅ Диагностика завершена успешно!")
        print("Ваш бот готов к работе с Google Calendar!")
        exit(0)