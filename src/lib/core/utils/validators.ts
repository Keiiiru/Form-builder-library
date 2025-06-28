export type ValidatorFn = (value: any) => string | null;

export const validators = {
  required:
    (message = "This field is required"): ValidatorFn =>
    (value) =>
      value !== undefined && value !== null && value !== "" ? null : message,

  minLength:
    (min: number, message = `Minimum length is ${min}`): ValidatorFn =>
    (value) =>
      typeof value === "string" && value.length >= min ? null : message,

  maxLength:
    (max: number, message = `Maximum length is ${max}`): ValidatorFn =>
    (value) =>
      typeof value === "string" && value.length <= max ? null : message,
};
