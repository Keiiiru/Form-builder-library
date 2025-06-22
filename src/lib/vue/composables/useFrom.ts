import { ref } from "vue";
import type { formField } from "@/lib/core/types";

export function useForm(schema: formField[]) {
  // Define form data record
  const formData = ref<Record<string, any>>({});

  // Define default values
  schema.forEach((field) => {
    switch (field.fieldType) {
      case "number":
        formData.value[field.name] = 0;
        break;
      case "text":
        formData.value[field.name] = "";
        break;
      default:
        formData.value[field.name] = "";
    }
  });

  return { formData };
}
