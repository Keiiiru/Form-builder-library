import { expect, describe, it, beforeEach } from "vitest";
import { validators } from "./validators";

describe("validators.ts", () => {
  it("should validate require", () => {
    expect(validators.required("this field is required")("")).toBe(
      "this field is required"
    );
    expect(validators.required("this field is required")("valid")).toBeNull();
  });

  it("should validate min length", () => {
    expect(validators.minLength(2, "min length: 2 char")("a")).toBe(
      "min length: 2 char"
    );
    expect(validators.minLength(2, "min length: 2 char")("asd")).toBeNull();
  });

  it("should validate max length", () => {
    expect(validators.maxLength(4, "max length: 4char")("testing")).toBe(
      "max length: 4char"
    );
    expect(validators.maxLength(4, "max length: 4char")("tes")).toBeNull();
  });
});
