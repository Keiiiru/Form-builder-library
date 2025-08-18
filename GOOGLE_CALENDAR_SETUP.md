# Настройка Google Calendar API для Telegram бота

## 🎯 Проблема
Если записи не появляются в календаре, скорее всего проблема в настройке Google Calendar API или правах доступа.

## 🔍 Диагностика
Сначала запустите диагностический скрипт:
```bash
python test_calendar.py
```

Этот скрипт покажет точную причину проблемы.

## ⚙️ Пошаговая настройка Google Calendar API

### Шаг 1: Создание проекта в Google Cloud Console

1. Перейдите на [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Запишите **Project ID** - он понадобится

### Шаг 2: Включение Google Calendar API

1. В Google Cloud Console перейдите в **APIs & Services** → **Library**
2. Найдите **Google Calendar API**
3. Нажмите **Enable**

### Шаг 3: Создание Service Account

1. Перейдите в **APIs & Services** → **Credentials**
2. Нажмите **Create Credentials** → **Service Account**
3. Заполните форму:
   - **Service account name**: `telegram-bot-calendar`
   - **Service account ID**: автоматически сгенерируется
   - **Description**: `Service account for Telegram booking bot`
4. Нажмите **Create and Continue**
5. На шаге **Grant this service account access to project** можно пропустить
6. Нажмите **Done**

### Шаг 4: Создание ключа для Service Account

1. В списке Service Accounts найдите созданный аккаунт
2. Нажмите на него
3. Перейдите на вкладку **Keys**
4. Нажмите **Add Key** → **Create New Key**
5. Выберите **JSON** формат
6. Нажмите **Create**
7. Файл автоматически скачается
8. **Переименуйте** файл в `aura-469414-e8af117aeedf.json`
9. **Поместите** файл в папку с ботом

### Шаг 5: Настройка доступа к календарю

**Это самый важный шаг!** Без него записи не будут создаваться.

1. Откройте скачанный JSON файл
2. Найдите поле `client_email` - это email вашего Service Account
3. Скопируйте этот email (например: `telegram-bot-calendar@project-123456.iam.gserviceaccount.com`)

4. Откройте [Google Calendar](https://calendar.google.com/)
5. В левой панели найдите календарь, в который хотите добавлять записи
6. Нажмите на три точки рядом с календарем → **Settings and sharing**
7. Прокрутите до раздела **Share with specific people**
8. Нажмите **Add people**
9. Вставьте email Service Account
10. Выберите права доступа: **Make changes to events** (или **Make changes and manage sharing**)
11. Нажмите **Send**

### Шаг 6: Получение Calendar ID

1. В настройках календаря прокрутите до раздела **Integrate calendar**
2. Скопируйте **Calendar ID**
3. Если используете основной календарь, ID будет ваш email или можно использовать `"primary"`

### Шаг 7: Обновление кода

В файле `telegram_booking_bot.py` обновите:

```python
CALENDAR_ID = "ваш_calendar_id_здесь"  # или "primary" для основного календаря
```

## 🚀 Проверка настройки

1. Запустите диагностику:
```bash
python test_calendar.py
```

2. Если все настроено правильно, вы увидите:
```
✅ Все тесты пройдены успешно!
✅ Google Calendar API работает корректно
✅ Права доступа настроены правильно
✅ Бот может создавать события в календаре
```

3. Запустите бота:
```bash
python telegram_booking_bot.py
```

4. В боте используйте команду `/test_calendar` для дополнительной проверки

## 🐛 Частые ошибки и решения

### Ошибка 403 (Forbidden)
**Причина**: Service Account не имеет прав на календарь
**Решение**: Повторите Шаг 5 - добавьте email Service Account в настройки календаря

### Ошибка 404 (Not Found)
**Причина**: Неправильный Calendar ID
**Решение**: Проверьте Calendar ID в настройках календаря

### "Файл учетных данных не найден"
**Причина**: JSON файл не в той папке или неправильное имя
**Решение**: Убедитесь, что файл называется `aura-469414-e8af117aeedf.json` и находится рядом с ботом

### "Календары не найдены"
**Причина**: Service Account не добавлен ни в один календарь
**Решение**: Добавьте Service Account в календарь (Шаг 5)

## 📋 Проверочный список

- [ ] Google Calendar API включен в проекте
- [ ] Service Account создан
- [ ] JSON ключ скачан и переименован
- [ ] JSON файл в папке с ботом
- [ ] Email Service Account добавлен в календарь с правами редактирования
- [ ] Calendar ID правильный
- [ ] Диагностический скрипт проходит успешно
- [ ] Команда `/test_calendar` в боте работает

## 🔗 Полезные ссылки

- [Google Calendar API Documentation](https://developers.google.com/calendar/api/guides/overview)
- [Service Accounts Guide](https://cloud.google.com/iam/docs/service-accounts)
- [Calendar API Python Quickstart](https://developers.google.com/calendar/api/quickstart/python)