import {
  CheckBoxField,
  FormField,
  NumberField,
  SelectorField,
  TextField,
} from "../model";

export class SchemaBuilder {
  private schema: FormField[];

  constructor() {
    this.schema = [];
  }

  text(params: TextField) {
    this.schema.push({
      ...params,
      fieldType: "text",
    });
    return this;
  }

  number(params: NumberField): this {
    this.schema.push({
      ...params,
      fieldType: "number",
    });
    return this;
  }

  checkbox(params: CheckBoxField): this {
    this.schema.push({
      ...params,
      fieldType: "checkBox",
    });
    return this;
  }

  selector(params: SelectorField): this {
    this.schema.push({
      ...params,
      fieldType: "selector",
    });

    return this;
  }

  build() {
    return [...this.schema];
  }
}
