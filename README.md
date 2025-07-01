# form-builder-library

Библиотека для динамического построения и валидации форм на основе схемы.  
Позволяет создавать поля разных типов, добавлять кастомные валидаторы и работать с данными формы.

---

## Установка

```bash
npm install form-builder-library
```

или

```bash
yarn add form-builder-library
```

---

## Быстрый старт

```ts
import { SchemaBuilder } from "form-builder-library";

const schema = new SchemaBuilder()
  .text({ name: "username", label: "Username" })
  .number({ name: "age", label: "Age" })
  .checkbox({ name: "agree", label: "Agree to terms" })
  .selector({ name: "gender", label: "Gender", options: ["male", "female"] })
  .build();

console.log(schema);
/* 
[
  { name: "username", label: "Username", fieldType: "text" },
  { name: "age", label: "Age", fieldType: "number" },
  { name: "agree", label: "Agree to terms", fieldType: "checkBox" },
  { name: "gender", label: "Gender", fieldType: "selector", options: ["male", "female"] }
]
*/
```

---

## API

### Класс `SchemaBuilder`

Используется для пошагового построения схемы формы.

#### Методы

- `text(config: FieldConfig): this` — Добавить текстовое поле  
- `number(config: FieldConfig): this` — Добавить числовое поле  
- `checkbox(config: FieldConfig): this` — Добавить чекбокс  
- `selector(config: SelectorFieldConfig): this` — Добавить селектор с опциями  
- `build(): FormField[]` — Вернуть готовую схему формы в виде массива полей

#### Конфигурация поля `FieldConfig`

```ts
{
  name: string; // уникальный идентификатор поля
  label: string; // название поля, отображаемое пользователю
  placeholder?: string; // (опционально) плейсхолдер для полей ввода
  validator?: ValidatorFn; // (опционально) функция-валидатор
}
```

#### Конфигурация селектора `SelectorFieldConfig`

Расширяет `FieldConfig`:

```ts
{
  options: string[]; // список опций для выпадающего списка
}
```

---

### Тип `ValidatorFn`

Функция валидации принимает значение и возвращает либо сообщение об ошибке (строку), либо `null`, если значение валидно.

```ts
type ValidatorFn = (value: any) => string | null;
```

---

### Встроенные валидаторы

В библиотеке есть набор часто используемых валидаторов:

```ts
import { validators } from "form-builder-library";

validators.required("Поле обязательно для заполнения");
validators.minLength(5, "Минимальная длина 5 символов");
validators.maxLength(20, "Максимальная длина 20 символов");
```

---

## Пример использования с Vue 3

```vue
<template>
  <form @submit.prevent="submitForm">
    <FieldRenderer
      v-for="field in schema"
      :key="field.name"
      :field="field"
      v-model="formData[field.name]"
      :error="errors[field.name]"
    />
    <button type="submit">Отправить</button>
  </form>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { SchemaBuilder, validators } from "form-builder-library";
import FieldRenderer from "./FieldRenderer.vue";

const schema = new SchemaBuilder()
  .text({ name: "username", label: "Имя пользователя", validator: validators.required() })
  .number({ name: "age", label: "Возраст" })
  .checkbox({ name: "subscribe", label: "Подписаться на новости" })
  .selector({ name: "gender", label: "Пол", options: ["Мужской", "Женский"] })
  .build();

const formData = ref({});
const errors = ref({});

function validateField(name, value) {
  const field = schema.find(f => f.name === name);
  if (field?.validator) return field.validator(value);
  return null;
}

function submitForm() {
  let valid = true;
  errors.value = {};
  for (const field of schema) {
    const error = validateField(field.name, formData.value[field.name]);
    if (error) valid = false;
    errors.value[field.name] = error;
  }
  if (valid) {
    alert("Форма валидна! Отправляем данные...");
    // отправка данных
  }
}
</script>
```

---

## Тестирование

В проекте используется [Vitest](https://vitest.dev/) для написания юнит-тестов.

Запустить тесты:

```bash
npm run test
```

---

## Вклад и предложения

Пожалуйста, открывайте issue и pull request для предложений и исправлений.

---

## Лицензия

MIT

---

Если нужна помощь с интеграцией, примерами или расширением функционала — обращайся!  
Удачи с проектом! 🚀
