<template>
  <div class="field">
    <label class="label">{{ field.label }}</label>

    <!-- Text field -->
    <input type="text" v-if="field.fieldType === 'text'" v-model="value" />

    <!-- Number filed -->
    <input type="number" v-if="field.fieldType === 'number'" v-model="value" />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { formField } from "@/lib/core/types";

const props = defineProps<{
  field: formField;
  modelValue: any;
}>();

const emit = defineEmits(["update:modelValue"]);

const value = computed({
  get: () => props.modelValue,
  set: (val) => emit("update:modelValue", val),
});
</script>

<style scoped></style>
