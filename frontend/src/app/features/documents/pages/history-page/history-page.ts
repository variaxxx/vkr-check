import { ChangeDetectionStrategy, Component, DestroyRef, inject, OnInit, signal } from "@angular/core";
import { takeUntilDestroyed, toObservable } from "@angular/core/rxjs-interop";
import { FormControl, FormGroup, ReactiveFormsModule } from "@angular/forms";
import { ActivatedRoute, Router } from "@angular/router";
import { DocumentService } from "@core/services";
import { Button } from "@shared/components/button/button";
import { Icon } from "@shared/components/icon/icon";
import { Select, SelectOption } from "@shared/components/select/select";
import { DOCUMENT_STATUS, DocumentStatus } from "@shared/enums";
import { combineLatest, debounceTime, distinctUntilChanged, startWith, Subject, switchMap, tap } from "rxjs";

import { DocumentShortResponse } from "../../dto";
import { DocumentsList } from "./components/documents-list/documents-list";
import { SearchField } from "./components/search-field/search-field";

@Component({
  selector: "app-history-page",
  imports: [SearchField, Select, ReactiveFormsModule, DocumentsList, Button, Icon],
  templateUrl: "./history-page.html",
  styleUrl: "./history-page.scss",
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HistoryPage implements OnInit {
  private readonly docService = inject(DocumentService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  public filterOptions: SelectOption[] = [
    { label: "Все статусы", value: "" },
    { label: "Загружен", value: DOCUMENT_STATUS.UPLOADED },
    { label: "В обработке", value: DOCUMENT_STATUS.IN_PROCESSING },
    { label: "Ошибка", value: DOCUMENT_STATUS.FAILED },
    { label: "Зачёт", value: DOCUMENT_STATUS.APPROVED },
    { label: "Незачёт", value: DOCUMENT_STATUS.REJECTED },
  ];

  public form = new FormGroup({
    status: new FormControl<DocumentStatus | "">(""),
    query: new FormControl<string>(""),
  });

  protected page = signal<number>(1);
  protected page$ = toObservable(this.page);
  protected total = signal<number | undefined>(undefined);
  protected documents = signal<DocumentShortResponse[] | undefined>(undefined);
  protected isUpdating = signal<boolean>(true);

  protected pageSize = 20;
  private update$ = new Subject<void>();

  protected update(): void {
    this.update$.next(void 0);
  }

  ngOnInit(): void {
    const params = this.route.snapshot.queryParams;

    this.form.patchValue({
      // eslint-disable-next-line dot-notation
      status: params["status"] || "",
      // eslint-disable-next-line dot-notation
      query: params["query"] || "",
    });

    // eslint-disable-next-line dot-notation
    this.page.set(+params["page"] || 1);

    combineLatest([
      this.form.valueChanges.pipe(
        startWith(this.form.value),
        debounceTime(300),
        distinctUntilChanged(
          (a, b) => JSON.stringify(a) === JSON.stringify(b),
        ),
      ),
      this.page$.pipe(
        startWith(this.page()),
      ),
      this.update$.pipe(
        startWith(void 0),
      ),
    ])
      .pipe(
        takeUntilDestroyed(this.destroyRef),

        tap(([filters, page]) => {
          this.isUpdating.set(true);
          this.documents.set(undefined);
          this.total.set(undefined);

          this.router.navigate([], {
            queryParams: {
              status: filters.status || undefined,
              query: filters.query || undefined,
              page,
            },
          });
        }),

        switchMap(([filters, page]) => this.docService.findMany({
          limit: this.pageSize,
          offset: this.pageSize * (page - 1),
          status: filters.status || undefined,
          query: filters.query?.trim() || undefined,
        })),

        tap((val) => {
          this.isUpdating.set(false);
          this.documents.set(val.items);
          this.total.set(val.total);

          if (val.total <= (this.page() - 1) * this.pageSize)
            this.page.set(1);
        }),
      )
      .subscribe();
  }
}
