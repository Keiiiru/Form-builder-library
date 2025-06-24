import { expect, describe, it } from "vitest";
import { mount } from "@vue/test-utils";
import FieldRenderer from "./FieldRenderer.vue";

describe("FieldRenderer", () => {
  it("Should render TextField and emit update ", () => {
    const wrapper = mount(FieldRenderer, {
      props: {
        field: {
          name: "username",
          label: "Username",
          fieldType: "text",
        },
        modelValue: "",
        error: "",
      },
    });

    expect(wrapper.find("label").exists()).toBe(true);
    expect(wrapper.find("label").text()).toEqual("Username");

    const input = wrapper.find("input");
    input.setValue("John");

    expect(wrapper.emitted("update:modelValue")).toBeTruthy();
    expect(wrapper.emitted("update:modelValue")?.[0]).toEqual(["John"]);
  });

  it("Should render NumberField and emit update", () => {
    const wrapper = mount(FieldRenderer, {
      props: {
        field: {
          name: "age",
          label: "Age",
          fieldType: "number",
        },
        modelValue: "",
        error: "",
      },
    });

    expect(wrapper.find("label").exists()).toBe(true);
    expect(wrapper.find("label").text()).toEqual("Age");

    const input = wrapper.find("input");
    input.setValue(10);

    expect(wrapper.emitted("update:modelValue")).toBeTruthy();
    expect(wrapper.emitted("update:modelValue")?.[0]).toEqual([10]);
  });

  it("Should render CheckBox and emit update", () => {
    const wrapper = mount(FieldRenderer, {
      props: {
        field: {
          name: "agree",
          label: "Agree",
          fieldType: "checkBox",
        },
        modelValue: "",
        error: "",
      },
    });

    expect(wrapper.find("label").exists()).toBe(true);
    expect(wrapper.find("label").text()).toEqual("Agree");

    const input = wrapper.find("input");
    input.setValue(true);

    expect(wrapper.emitted("update:modelValue")).toBeTruthy();
    expect(wrapper.emitted("update:modelValue")?.[0]).toEqual([true]);
  });

  it("Should render Selector and emit update", () => {
    const wrapper = mount(FieldRenderer, {
      props: {
        field: {
          name: "gender",
          label: "Gender",
          fieldType: "selector",
          options: ["male", "female"],
        },
        modelValue: "",
        error: "",
      },
    });

    expect(wrapper.find("label").exists()).toBe(true);
    expect(wrapper.find("label").text()).toEqual("Gender");

    const select = wrapper.find("select");
    select.setValue("female");

    expect(wrapper.emitted("update:modelValue")).toBeTruthy();
    expect(wrapper.emitted("update:modelValue")?.[0]).toEqual(["female"]);
  });

  it("Should render error text", () => {
    const wrapper = mount(FieldRenderer, {
      props: {
        field: {
          name: "username",
          label: "Username",
          fieldType: "text",
        },
        modelValue: "",
        error: "This field is required",
      },
    });

    expect(wrapper.find("p").exists()).toBe(true);
    expect(wrapper.find("p").text()).toEqual("This field is required");
  });
});
