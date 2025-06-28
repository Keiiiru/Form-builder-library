type fieldTypes = "text" | "number" | "selector" | "checkBox" | "unknown";

export interface FormField {
  fieldType: fieldTypes;
  name: string;
  label: string;
  placeholder?: string;
  options?: string[];
  validator?: (value: any) => null | string;
}

export type TextField = Pick<
  FormField,
  "name" | "label" | "placeholder" | "validator"
>;

export type NumberField = Pick<
  FormField,
  "name" | "label" | "placeholder" | "validator"
>;

export type CheckBoxField = Pick<FormField, "name" | "label" | "validator">;

export type SelectorField = Pick<
  FormField,
  "name" | "label" | "options" | "validator"
>;
