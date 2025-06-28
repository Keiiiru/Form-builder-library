<template>
  <form @submit="submit">
    <FieldRenderer
      v-for="field in schema"
      :key="field.name"
      :field="field"
      :modelValue="formData[field.name]"
      :error="errors[field.name] || null"
      @update:modelValue="(value) => onFieldUpdate(field.name, value)"
    />

    <button type="submit">Submit</button>
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
