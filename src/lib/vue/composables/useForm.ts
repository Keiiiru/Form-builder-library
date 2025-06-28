import { ref } from "vue";
import type { FormField } from "@/lib/core/model";
import { initForm } from "@/lib/core/utils/init-form";

export function useForm(schema: FormField[]) {
  // Define form data record
  const formData = ref<Record<string, any>>(initForm(schema));

  return { formData };
}
