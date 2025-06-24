type fieldTypes = "text" | "number" | "selector" | "checkBox" | "unknown";

export interface formField {
  fieldType: fieldTypes;
  name: string;
  label: string;
  placeholder?: string;
  options?: string[];
  validator?: (value: any) => null | string;
}
