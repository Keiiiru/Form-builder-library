type fieldTypes = "text" | "number" | "selector" | "checkBox";

export interface formField {
  fieldType: fieldTypes;
  name: string;
  label: string;
  placeholder?: string;
  options?: string[];
  validator?: (value: any) => null | string;
}
