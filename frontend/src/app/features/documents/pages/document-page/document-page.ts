import { DatePipe, Location } from "@angular/common";
import { ChangeDetectionStrategy, Component, DestroyRef, inject, OnInit, signal } from "@angular/core";
import { takeUntilDestroyed } from "@angular/core/rxjs-interop";
import { ActivatedRoute, Router } from "@angular/router";
import { DocumentService, NotificationService } from "@core/services";
import { ReportsService } from "@core/services/reports.service";
import { Button } from "@shared/components/button/button";
import { DocumentStatusPlate } from "@shared/components/document-status-plate/document-status-plate";
import { Icon } from "@shared/components/icon/icon";
import { NgxSkeletonLoaderModule } from "ngx-skeleton-loader";
import { catchError, of, tap, throwError } from "rxjs";

import { DocumentResponse } from "../../dto";
import { AnalysisList } from "./components/analysis-list/analysis-list";
import { EvaluationsList } from "./components/evaluations-list/evaluations-list";

@Component({
  selector: "app-document-page",
  imports: [Icon, DocumentStatusPlate, DatePipe, NgxSkeletonLoaderModule, EvaluationsList, AnalysisList, Button],
  templateUrl: "./document-page.html",
  styleUrl: "./document-page.scss",
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DocumentPage implements OnInit {
  private readonly location = inject(Location);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  private readonly docService = inject(DocumentService);
  private readonly repService = inject(ReportsService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly notificationService = inject(NotificationService);

  protected document = signal<DocumentResponse | null>(null);

  protected back(): void {
    this.location.back();
  }

  protected downloadDoc(
    event: MouseEvent,
  ): any {
    event.stopPropagation();

    return this.docService.download(
      this.document()!.id,
      this.document()!.original_name,
    ).subscribe();
  }

  protected downloadRep(
    event: MouseEvent,
  ): any {
    event.stopPropagation();

    return this.repService.downloadForDoc(
      this.document()!.id,
    ).pipe(
      tap((report) => {
        const url = URL.createObjectURL(report);

        const a = document.createElement("a");
        a.href = url;
        a.download = "report.pdf";
        a.click();

        URL.revokeObjectURL(url);
      }),
    ).subscribe();
  }

  ngOnInit(): void {
    // eslint-disable-next-line dot-notation
    const docId = this.route.snapshot.params["docId"];
    this.docService.findById(docId).pipe(
      takeUntilDestroyed(this.destroyRef),
      catchError((err) => {
        if (err.status === 404) {
          this.router.navigateByUrl("/");
          this.notificationService.error("Работа не найдена");
          return of(null);
        }
        return throwError(() => err);
      }),
      tap(val => this.document.set(val)),
    ).subscribe();
  }
}
