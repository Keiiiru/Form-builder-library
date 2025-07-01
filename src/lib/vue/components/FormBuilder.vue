<template>
  <form class="form-builder-form" @submit="submit">
    <FieldRenderer
      v-for="field in schema"
      :key="field.name"
      :field="field"
      :modelValue="formData[field.name]"
      :error="errors[field.name] || null"
      @update:modelValue="(value) => onFieldUpdate(field.name, value)"
      class="field-renderer"
    />

    <button type="submit" class="submit-btn">Submit</button>
  </form>
</template>

<script setup lang="ts">
import type { FormField } from "@/lib/core/model";
import { useForm } from "@/lib/vue/composables/useForm";
import FieldRenderer from "./FieldRenderer.vue";
import { Ref, ref } from "vue";

const props = defineProps<{
  schema: FormField[];
  submitForm: (payload: Record<string, any>) => void;
}>();

const { formData } = useForm(props.schema);
const errors = ref<Record<string, string | null>>({});

const validateField = (fieldName: string, value: any): string | null => {
  const field = props.schema.find((f) => f.name === fieldName);
  if (field?.validator) {
    return field.validator(value) || null;
  }
  return null;
};

const onFieldUpdate = (fieldName: string, newValue: any) => {
  formData.value[fieldName] = newValue;
  errors.value[fieldName] = validateField(fieldName, newValue);
};

const validateAll = (): boolean => {
  let isValid = true;
  for (const field of props.schema) {
    const error = validateField(field.name, formData.value[field.name]);
    errors.value[field.name] = error;
    if (error) isValid = false;
  }
  return isValid;
};

const submit = (e: Event) => {
  e.preventDefault();
  if (validateAll()) {
    props.submitForm(formData.value);
  }
};
</script>

<style scoped>
.form-builder-form {
  max-width: 400px;
  margin: 1rem auto;
  padding: 1rem 1.25rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  background: #fafafa;
  box-shadow: 0 2px 6px rgb(0 0 0 / 0.1);
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.field-renderer {
  /* Отступы и границы для каждого поля */
  padding: 0.75rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  box-shadow: 0 1px 2px rgb(0 0 0 / 0.05);
  transition: box-shadow 0.2s ease;
}

.field-renderer:hover {
  box-shadow: 0 2px 6px rgb(0 0 0 / 0.1);
}

.submit-btn {
  align-self: flex-end;
  padding: 0.6rem 1.2rem;
  font-size: 1rem;
  font-weight: 600;
  color: white;
  background-color: #3498db;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  user-select: none;
  transition: background-color 0.25s ease;
}

.submit-btn:hover {
  background-color: #2980b9;
}

.submit-btn:disabled {
  background-color: #9bbbd4;
  cursor: not-allowed;
}
</style>
