import { expect, describe, it, beforeEach } from "vitest";
import { SchemaBuilder } from "./schema-builder";

describe("schema-builder", () => {
  let schema: SchemaBuilder;
  beforeEach(() => {
    schema = new SchemaBuilder();
  });
  it("build returns empty array for new schema", () => {
    expect(schema.build()).toEqual([]);
  });

  it("text adds a text field to the schema", () => {
    schema.text({
      name: "name",
      label: "name",
    });

    expect(schema.build()).toEqual([
      { name: "name", label: "name", fieldType: "text" },
    ]);
  });

  it("build returns all fields added via chain methods", () => {
    schema
      .text({
        name: "name",
        label: "name",
      })
      .number({ name: "age", label: "age" })
      .checkbox({
        name: "agree",
        label: "agree",
      })
      .selector({
        name: "gender",
        label: "gender",
        options: ["male", "female"],
      });

    expect(schema.build()).toEqual([
      { name: "name", label: "name", fieldType: "text" },
      { name: "age", label: "age", fieldType: "number" },
      { name: "agree", label: "agree", fieldType: "checkBox" },
      {
        name: "gender",
        label: "gender",
        fieldType: "selector",
        options: ["male", "female"],
      },
    ]);
  });
});
