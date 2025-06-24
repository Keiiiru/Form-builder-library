import { formField } from "@/lib/core/types";
import { expect, describe, it } from "vitest";
import { useForm } from "./useForm";

const formSchema: formField[] = [
  {
    name: "username",
    label: "Username",
    fieldType: "text",
    placeholder: "Type username",
  },
  {
    name: "age",
    label: "age",
    fieldType: "number",
    placeholder: "Type age",
  },
  {
    name: "gender",
    label: "gender",
    fieldType: "selector",
    options: ["male", "female"],
    placeholder: "choose gender",
  },
  {
    name: "agree",
    label: "agree policy privacy",
    fieldType: "checkBox",
  },
];

describe("useForm", () => {
  it("should initialize formData with default values", () => {
    const { formData } = useForm(formSchema);

    expect(formData.value).toEqual({
      username: "",
      age: 0,
      gender: "Select",
      agree: false,
    });
  });

  it("should have equal keys", () => {
    const { formData } = useForm(formSchema);

    expect(Object.keys(formData.value)).toEqual([
      "username",
      "age",
      "gender",
      "agree",
    ]);
  });

  it("should initialize field with empty data for unknown fieldType", () => {
    const { formData } = useForm([
      {
        name: "field",
        label: "field",
        fieldType: "unknown",
      },
    ]);

    expect(formData.value).toEqual({ field: "" });
  });
});
