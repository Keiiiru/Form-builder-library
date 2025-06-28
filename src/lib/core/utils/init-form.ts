import { FormField } from "../model";

export function initForm(schema: FormField[]): Object {
  const formData: Record<string, any> = {};

  schema.forEach((field) => {
    switch (field.fieldType) {
      case "number":
        formData[field.name] = 0;
        break;
      case "text":
        formData[field.name] = "";
        break;
      case "selector":
        formData[field.name] = "Select";
        break;
      case "checkBox":
        formData[field.name] = false;
        break;
      default:
        formData[field.name] = "";
    }
  });

  return formData;
}
