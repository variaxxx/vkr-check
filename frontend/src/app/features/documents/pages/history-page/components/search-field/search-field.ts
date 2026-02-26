import { ChangeDetectionStrategy, Component, forwardRef, signal } from "@angular/core";
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from "@angular/forms";
import { Icon } from "@shared/components/icon/icon";

@Component({
  selector: "app-search-field",
  imports: [Icon],
  templateUrl: "./search-field.html",
  styleUrl: "./search-field.scss",
  changeDetection: ChangeDetectionStrategy.OnPush,
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => SearchField),
      multi: true,
    },
  ],
})
export class SearchField implements ControlValueAccessor {
  protected query = signal<string | null>(null);

  protected input(
    value: any,
  ): void {
    this.query.set(value);
    this.onChange(value);
    this.onTouched();
  }

  protected clear(
    event: MouseEvent,
  ): void {
    event.stopPropagation();

    this.input("");
  }

  registerOnChange(fn: any): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: any): void {
    this.onTouched = fn;
  }

  writeValue(obj: string): void {
    this.query.set(obj);
  }

  onChange = (value: any): void => {};
  onTouched = (): void => {};
}
