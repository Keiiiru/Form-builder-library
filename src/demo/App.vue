<template>
  <div>
    <h1 class="user-form">Form demo</h1>
    <FormBuilder :schema="formSchema" />
  </div>
</template>

<script setup lang="ts">
import type { formField } from "../lib/core";
import FormBuilder from "../lib/vue";

const formSchema: formField[] = [
  {
    name: "username",
    label: "Username",
    fieldType: "text",
  },
  {
    name: "age",
    label: "age",
    fieldType: "number",
  },
];
</script>

<style scoped></style>
