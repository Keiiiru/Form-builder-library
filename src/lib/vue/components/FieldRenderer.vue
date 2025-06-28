<template>
  <div class="field">
    <label class="label">{{ field.label }}</label>

    <!-- Text field -->
    <input
      :name="field.name"
      type="text"
      v-if="field.fieldType === 'text'"
      v-model="value"
      :placeholder="field.placeholder"
    />

    <!-- Number filed -->
    <input
      :name="field.name"
      type="number"
      v-if="field.fieldType === 'number'"
      v-model="value"
      :placeholder="field.placeholder"
    />

    <!-- Selector field -->
    <select
      v-if="field.fieldType === 'selector'"
      v-model="value"
      :name="field.name"
    >
      <option v-for="option in field.options" :value="option">
        {{ option }}
      </option>
    </select>

    <input
      type="checkbox"
      :name="field.name"
      :id="field.name"
      v-model="value"
      v-if="field.fieldType === 'checkBox'"
    />

    <p v-if="error" class="error-text">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { formField } from "@/lib/core/model";

const props = defineProps<{
  field: formField;
  modelValue: any;
  error: string | null;
}>();

const emit = defineEmits(["update:modelValue"]);

const value = computed({
  get: () => props.modelValue,
  set: (val) => emit("update:modelValue", val),
});
</script>

<style scoped></style>
