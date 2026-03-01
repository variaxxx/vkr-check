import { ChangeDetectionStrategy, Component, inject } from "@angular/core";
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from "@angular/forms";
import { provideNativeDateAdapter } from "@angular/material/core";
import { MatDatepickerModule } from "@angular/material/datepicker";
import { MatFormFieldModule } from "@angular/material/form-field";
import { NotificationService } from "@core/services";
import { ReportsService } from "@core/services/reports.service";
import { Button } from "@shared/components/button/button";
import { Icon } from "@shared/components/icon/icon";
import { tap } from "rxjs";

@Component({
  selector: "app-report-page",
  providers: [provideNativeDateAdapter()],
  imports: [Button, MatDatepickerModule, MatFormFieldModule, ReactiveFormsModule, Icon],
  templateUrl: "./report-page.html",
  styleUrl: "./report-page.scss",
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ReportPage {
  private readonly reportsService = inject(ReportsService);
  private readonly notificationService = inject(NotificationService);

  protected download(
    event: MouseEvent,
  ): void {
    event.stopPropagation();

    if (!this.range.valid || (this.range.controls.start.value && this.range.controls.start.value > new Date()))
      return this.notificationService.error("Укажите корректный период");

    this.reportsService.downloadForAll({
      start: this.range.value.start!,
      end: this.range.value.end!,
    }).pipe(
      tap((report) => {
        const url = URL.createObjectURL(report);

        const a = document.createElement("a");
        a.href = url;
        a.download = "report.xlsx";
        a.click();

        URL.revokeObjectURL(url);
      }),
    ).subscribe({
      error: () => {
        this.notificationService.error("Ошибка при загрузке отчёта");
      },
    });
  }

  protected readonly range = new FormGroup({
    start: new FormControl<Date | null>(null, [Validators.required]),
    end: new FormControl<Date | null>(null, [Validators.required]),
  });
}
