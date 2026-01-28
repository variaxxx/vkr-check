import { Icon } from "../icon/icon";
import { ChangeDetectionStrategy, Component, forwardRef, input, signal } from "@angular/core";
import { ControlValueAccessor, FormsModule, NG_VALUE_ACCESSOR } from "@angular/forms";

export interface SelectOption {
  label: string;
  value: any;
}

@Component({
  selector: "app-select",
  imports: [Icon, FormsModule],
  templateUrl: "./select.html",
  styleUrl: "./select.scss",
  changeDetection: ChangeDetectionStrategy.OnPush,
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => Select),
      multi: true,
    },
  ],
})
export class Select implements ControlValueAccessor {
  public options = input.required<SelectOption[]>();

  protected selectedOption = signal<any>(undefined);

  public select(
    value: any,
  ): void {
    this.selectedOption.set(value);
    this.onChange(value);
    this.onTouched();
  }

  registerOnChange(fn: any): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: any): void {
    this.onTouched = fn;
  }

  writeValue(obj: any): void {
    this.selectedOption.set(obj);
    console.log(obj, this.selectedOption());
  }

  onChange = (value: any): void => {};
  onTouched = (): void => {};
}
