<template>
  <div>
    <h1 class="user-form">Form demo</h1>
    <FormBuilder :schema="formSchema" :submit-form="submit" />
  </div>
</template>

<script setup lang="ts">
import { SchemaBuilder } from "@/lib/core/utils/schema-builder";
import FormBuilder from "../lib/vue";

const usernameValidator = (value: string): string | null => {
  if (value.length === 0) {
    return "This field is required";
  } else {
    return null;
  }
};

const formSchema = new SchemaBuilder()
  .text({
    name: "username",
    label: "Username",
    placeholder: "Type username",
    validator: usernameValidator,
  })
  .number({
    name: "age",
    label: "age",
    placeholder: "Type age",
  })
  .selector({
    name: "gender",
    label: "gender",
    options: ["male", "female"],
  })
  .checkbox({
    name: "agree",
    label: "agree policy privacy",
  })
  .build();

const submit = (formData: Record<string, any>) => {
  console.log(JSON.stringify(formData));
};
</script>

<style scoped></style>
