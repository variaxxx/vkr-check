import { Pipe, PipeTransform } from "@angular/core";

@Pipe({
  name: "prettyDate",
  standalone: true,
})
export class PrettyDatePipe implements PipeTransform {
  transform(value: Date | string | number, withTime = true): string {
    if (!value)
      return "";

    const date = new Date(value);

    const options: Intl.DateTimeFormatOptions = {
      day: "numeric",
      month: "long",
      year: "numeric",
      ...(withTime ? { hour: "2-digit", minute: "2-digit" } : {}),
    };

    return new Intl.DateTimeFormat("ru-RU", options).format(date);
  }
}
