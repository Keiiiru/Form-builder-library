# 🚨 Исправление конфликта модулей

## Проблема
Ошибка: `module 'calendar' has no attribute 'timegm'` означает, что в вашей папке есть файл `calendar.py`, который конфликтует со стандартным модулем Python `calendar`.

## 🔧 Быстрое решение

### Шаг 1: Найдите конфликтующий файл
В папке `/Users/mwosswq/code/aura-bot` найдите файл `calendar.py`

### Шаг 2: Переименуйте файл
```bash
cd /Users/mwosswq/code/aura-bot
mv calendar.py my_calendar.py
```

### Шаг 3: Обновите импорты (если нужно)
Если в других файлах есть `import calendar` или `from calendar import ...`, замените на:
```python
import my_calendar
# или
from my_calendar import ...
```

### Шаг 4: Запустите диагностику снова
```bash
python test_calendar.py
```

## 🔍 Автоматическая проверка

Теперь оба скрипта (`telegram_booking_bot.py` и `test_calendar.py`) автоматически проверяют наличие конфликтующих файлов и покажут, какие именно файлы нужно переименовать.

## 📋 Другие возможные конфликты

Убедитесь, что у вас нет файлов с такими именами:
- `calendar.py` → переименуйте в `my_calendar.py`
- `datetime.py` → переименуйте в `my_datetime.py`
- `json.py` → переименуйте в `my_json.py`
- `os.py` → переименуйте в `my_os.py`
- `time.py` → переименуйте в `my_time.py`
- `email.py` → переименуйте в `my_email.py`
- `asyncio.py` → переименуйте в `my_asyncio.py`

## ✅ После исправления

1. Запустите диагностику: `python test_calendar.py`
2. Если все ОК, запустите бота: `python telegram_booking_bot.py`
3. В боте проверьте командой `/test_calendar`

## 💡 Почему это происходит?

Python ищет модули сначала в текущей директории, потом в стандартных библиотеках. Если в вашей папке есть файл `calendar.py`, Python импортирует его вместо стандартного модуля `calendar`, что приводит к ошибкам.