import os
import datetime
import json
from typing import Optional

import pytz
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# --- Конфигурация ---
# Можно переопределить через переменные окружения:
#   GOOGLE_CREDENTIALS_FILE, CALENDAR_ID, IMPERSONATE_SUBJECT
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "aura-469414-e8af117aeedf.json")
CALENDAR_ID = os.getenv("CALENDAR_ID", "decembeeerrr@gmail.com")

# Если у вас Google Workspace и настроена делегация на уровне домена,
# укажите email пользователя для имп رسонации (with_subject).
IMPERSONATE_SUBJECT = os.getenv("IMPERSONATE_SUBJECT")

SCOPES = ["https://www.googleapis.com/auth/calendar"]
MOSCOW_TZ = pytz.timezone("Europe/Moscow")


def load_credentials(credentials_file: str) -> service_account.Credentials:
    credentials = service_account.Credentials.from_service_account_file(
        credentials_file, scopes=SCOPES
    )
    if IMPERSONATE_SUBJECT:
        # Требует Google Workspace + включённую делегацию на уровне домена
        credentials = credentials.with_subject(IMPERSONATE_SUBJECT)
    return credentials


def build_calendar_service(credentials: service_account.Credentials):
    return build("calendar", "v3", credentials=credentials)


def read_service_account_meta(credentials_file: str) -> tuple[str, str]:
    with open(credentials_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("client_email", "unknown"), data.get("project_id", "unknown")


def ensure_calendar_access(service, calendar_id: str) -> bool:
    """
    Проверяем доступ к конкретному календарю напрямую через calendars.get.
    Если календарь доступен, пытаемся добавить его в список calendarList (не критично, но удобно).
    Возвращает True, если доступ есть и можно писать события.
    """
    try:
        calendar = service.calendars().get(calendarId=calendar_id).execute()
        # Пробуем добавить в список, чтобы появлялся в calendarList.list()
        try:
            service.calendarList().insert(body={"id": calendar_id}).execute()
        except HttpError as insert_err:
            # 409 / alreadyExists — ок, игнорируем; прочие — не критично
            pass
        return True
    except HttpError as error:
        # 404 — нет такого календаря, 403 — нет прав
        print(f"   ❌ Нет доступа к календарю '{calendar_id}': {error}")
        if hasattr(error, "resp") and error.resp is not None:
            status = getattr(error.resp, "status", None)
            if status == 404:
                print("   📄 Код: 404 — календарь не найден или id указан неверно")
            elif status == 403:
                print("   📄 Код: 403 — недостаточно прав. Нужно расшарить календарь на сервисный аккаунт")
        return False


def try_create_test_event(service, calendar_id: str) -> bool:
    now = datetime.datetime.now(MOSCOW_TZ)
    start_dt = now + datetime.timedelta(minutes=1)
    end_dt = start_dt + datetime.timedelta(minutes=5)

    test_event = {
        "summary": "ТЕСТ - Диагностика API",
        "description": f"Тестовое событие для проверки API\nСоздано: {now.strftime('%d.%m.%Y %H:%M:%S')}",
        "start": {"dateTime": start_dt.isoformat(), "timeZone": "Europe/Moscow"},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": "Europe/Moscow"},
    }

    print("   📝 Создание тестового события...")
    try:
        created = service.events().insert(calendarId=calendar_id, body=test_event).execute()
        event_id = created.get("id")
        event_link = created.get("htmlLink", "")
        print("   ✅ Событие создано")
        print(f"   🆔 ID: {event_id}")
        print(f"   🔗 Ссылка: {event_link}")
    except HttpError as error:
        print(f"   ❌ Ошибка при создании события: {error}")
        if hasattr(error, "resp") and error.resp is not None:
            print(f"   📄 Код ошибки: {getattr(error.resp, 'status', 'n/a')}")
            print(f"   📄 Причина: {getattr(error.resp, 'reason', 'n/a')}")
        content = getattr(error, "content", None)
        if content:
            try:
                print(f"   📄 Детали: {content.decode()}")
            except Exception:
                print("   📄 Детали: <недоступны>")
        return False

    # Чистим за собой тестовое событие
    try:
        print("   🗑️ Удаление тестового события...")
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        print("   ✅ Удалено")
    except Exception:
        print("   ⚠️ Не удалось удалить тестовое событие (не критично)")

    return True


def main() -> bool:
    print("🔍 Диагностика Google Calendar API")
    print("=" * 50)

    # 1) Файл с учётными данными
    print("\n1️⃣ Проверка файла учетных данных:")
    print(f"   📁 Текущая директория: {os.getcwd()}")
    print(f"   📄 Ищем файл: {GOOGLE_CREDENTIALS_FILE}")
    if not os.path.exists(GOOGLE_CREDENTIALS_FILE):
        print(f"   ❌ Файл {GOOGLE_CREDENTIALS_FILE} не найден!")
        print("   📋 JSON в директории:")
        for file in os.listdir("."):
            if file.endswith(".json"):
                print(f"      📄 {file}")
        print("\n💡 Решение:")
        print("   - Поместите JSON с ключом сервисного аккаунта рядом со скриптом")
        print("   - Либо укажите путь через переменную окружения GOOGLE_CREDENTIALS_FILE")
        return False
    else:
        print(f"   ✅ Файл найден: {GOOGLE_CREDENTIALS_FILE}")

    # 2) Загрузка ключа
    print("\n2️⃣ Загрузка учетных данных:")
    try:
        credentials = load_credentials(GOOGLE_CREDENTIALS_FILE)
        print("   ✅ Учетные данные загружены")
        service_email, project_id = read_service_account_meta(GOOGLE_CREDENTIALS_FILE)
        print(f"   📧 Сервисный аккаунт: {service_email}")
        print(f"   🏗️ ID проекта: {project_id}")
        if IMPERSONATE_SUBJECT:
            print(f"   👤 Имперсонация пользователя: {IMPERSONATE_SUBJECT}")
    except Exception as e:
        print(f"   ❌ Ошибка загрузки учетных данных: {e}")
        return False

    # 3) Инициализация API
    print("\n3️⃣ Инициализация Google Calendar API:")
    try:
        service = build_calendar_service(credentials)
        print("   ✅ API сервис создан")
    except Exception as e:
        print(f"   ❌ Ошибка создания API сервиса: {e}")
        return False

    # 4) Проверка конкретного календаря (без зависимости от calendarList)
    print("\n4️⃣ Проверка доступа к целевому календарю:")
    print(f"   🎯 CALENDAR_ID: {CALENDAR_ID}")
    has_access = ensure_calendar_access(service, CALENDAR_ID)
    if not has_access:
        print("\n💡 Что нужно сделать:")
        print("   - Если это личный @gmail.com календарь, ОТКРОЙТЕ его настройки → 'Доступ к календарю' → 'Поделиться с конкретными людьми' → добавьте email сервисного аккаунта и дайте права 'Вносить изменения в события'.")
        print("   - Для Google Workspace можно настроить делегацию на уровне домена и указать IMPERSONATE_SUBJECT.")
        print("   - Проверьте корректность CALENDAR_ID (обычно это email или строка формата 'xxxx@group.calendar.google.com').")
        return False

    # 5) Тестовая запись
    print("\n5️⃣ Тестирование создания события:")
    if not try_create_test_event(service, CALENDAR_ID):
        if not IMPERSONATE_SUBJECT:
            print("\n💡 Подсказка: при 403 на личном аккаунте необходим шаринг календаря на сервисный аккаунт.")
        return False

    # 6) Финал
    print("\n🎉 Все проверки пройдены!")
    print("✅ Доступ к календарю подтвержден")
    print("✅ Создание/удаление события работает")
    print("\n📋 Конфигурация:")
    print(f"   📄 Файл учетных данных: {GOOGLE_CREDENTIALS_FILE}")
    print(f"   📅 Календарь ID: {CALENDAR_ID}")
    print(f"   📧 Сервисный аккаунт: {service_email}")
    if IMPERSONATE_SUBJECT:
        print(f"   👤 Имперсонация: {IMPERSONATE_SUBJECT}")
    return True


if __name__ == "__main__":
    ok = main()
    if not ok:
        print("\n❌ Диагностика выявила проблемы. Исправьте и запустите снова.")
        raise SystemExit(1)
    print("\n✅ Диагностика завершена успешно. Можно использовать бот для записи в Google Calendar.")
    raise SystemExit(0)

