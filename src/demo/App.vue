<template>
  <div>
    <h1 class="user-form">Form demo</h1>
    <FormBuilder :schema="formSchema" :submit-form="submit" />
  </div>
</template>

<script setup lang="ts">
import { Ref } from "vue";
import type { formField } from "../lib/core";
import FormBuilder from "../lib/vue";

const usernameValidator = (value: string): string | null => {
  if (value.length === 0) {
    return "This field is required";
  } else {
    return null;
  }
};

const formSchema: formField[] = [
  {
    name: "username",
    label: "Username",
    fieldType: "text",
    placeholder: "Type username",
    validator: usernameValidator,
  },
  {
    name: "age",
    label: "age",
    fieldType: "number",
    placeholder: "Type age",
  },
  {
    name: "gender",
    label: "gender",
    fieldType: "selector",
    options: ["male", "female"],
    placeholder: "choose gender",
  },
  {
    name: "agree",
    label: "agree policy privacy",
    fieldType: "checkBox",
  },
];

const submit = (formData: Record<string, any>) => {
  console.log(JSON.stringify(formData));
};
</script>

<style scoped></style>
