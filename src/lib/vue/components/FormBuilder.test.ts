import { expect, describe, it, vi, type Mock } from "vitest";
import { mount } from "@vue/test-utils";
import FormBuilder from "./FormBuilder.vue";
import { formField } from "@/lib/core";
import * as hooks from "@/lib/vue/composables/useForm";
import { nextTick, ref } from "vue";

const formSchema: formField[] = [
  {
    name: "username",
    label: "Username",
    fieldType: "text",
    placeholder: "Type username",
    validator: (value: string) =>
      value.length > 0 ? null : "This field is required",
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

vi.mock("@/lib/vue/composables/useForm", () => ({
  useForm: vi.fn(),
}));

describe("FormBuilder", () => {
  it("test rendering form schema", async () => {
    vi.mocked(hooks.useForm).mockImplementation(() => ({
      formData: ref({}),
    }));
    const wrapper = mount(FormBuilder, {
      props: {
        schema: formSchema,
        submitForm: (payload: any) => console.log(payload),
      },
    });

    expect(wrapper.find("select")).toBeTruthy();

    const inputs = wrapper.findAll("input");
    expect(inputs.length).toEqual(3);

    const labels = wrapper.findAll("label");
    expect(labels.length).toEqual(4);
  });

  it("check is validators works", async () => {
    const wrapper = mount(FormBuilder, {
      props: {
        schema: [
          {
            name: "username",
            label: "Username",
            fieldType: "text",
            placeholder: "Type username",
            validator: (value: string) =>
              value.length > 0 ? null : "This field is required",
          },
        ],
        submitForm: (payload: any) => console.log(payload),
      },
    });

    await wrapper.find('input[name="username"]').setValue("");
    await wrapper.find("form").trigger("submit");

    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("This field is required");

    await wrapper.find('input[name="username"]').setValue("valid");
    await wrapper.find("form").trigger("submit");

    await wrapper.vm.$nextTick();

    expect(wrapper.text()).not.toContain("This field is required");
  });
});
