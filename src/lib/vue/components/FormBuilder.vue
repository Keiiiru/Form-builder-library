<template>
  <form>
    <FieldRenderer
      v-for="field in schema"
      :key="field.name"
      :field="field"
      :modelValue="formData[field.name]"
      @update:modelValue="formData[field.name] = $event"
    />
  </form>
  <pre>{{ formData }}</pre>
</template>

<script setup lang="ts">
import type { formField } from "@/lib/core/types";
import { useForm } from "@/lib/vue/composables/useFrom";
import FieldRenderer from "./FieldRenderer.vue";

const props = defineProps<{ schema: formField[] }>();

const { formData } = useForm(props.schema);
</script>

<style scoped></style>
