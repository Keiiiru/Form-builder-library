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
import type { FormField } from "@/lib/core/model";

const props = defineProps<{
  field: FormField;
  modelValue: any;
  error: string | null;
}>();

const emit = defineEmits(["update:modelValue"]);

const value = computed({
  get: () => props.modelValue,
  set: (val) => emit("update:modelValue", val),
});
</script>

<style scoped>
.field {
  display: flex;
  flex-direction: column;
  margin-bottom: 1rem;
  font-family: Arial, sans-serif;
}

.label {
  font-weight: 600;
  margin-bottom: 0.3rem;
  color: #333;
  font-size: 14px;
}

input[type="text"],
input[type="number"],
select {
  padding: 0.5rem 0.75rem;
  font-size: 14px;
  border: 1.5px solid #ccc;
  border-radius: 4px;
  transition: border-color 0.2s ease;
}

input[type="text"]:focus,
input[type="number"]:focus,
select:focus {
  border-color: #4a90e2;
  outline: none;
}

input[type="checkbox"] {
  width: 16px;
  height: 16px;
  margin-top: 6px;
  cursor: pointer;
}

.error-text {
  color: #d9534f; /* красный */
  font-size: 12px;
  margin-top: 0.25rem;
}
</style>
