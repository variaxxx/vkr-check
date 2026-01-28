import { env } from "../../../../../environments/environment";
import { DocumentStatusPlate } from "../../../../shared/components/document-status-plate/document-status-plate";
import { Icon } from "../../../../shared/components/icon/icon";
import { DocumentShortResponse } from "../../../documents/dto";
import { DatePipe } from "@angular/common";
import { HttpClient } from "@angular/common/http";
import { ChangeDetectionStrategy, Component, computed, inject, input, output } from "@angular/core";
import { RouterLink } from "@angular/router";
import { NgxSkeletonLoaderComponent } from "ngx-skeleton-loader";
import { tap } from "rxjs";

@Component({
  selector: "app-documents-list",
  imports: [Icon, DatePipe, NgxSkeletonLoaderComponent, RouterLink, DocumentStatusPlate],
  templateUrl: "./documents-list.html",
  styleUrl: "./documents-list.scss",
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DocumentsList {
  private readonly http = inject(HttpClient);

  public page = input.required<number>();
  public pageSize = input.required<number>();
  public total = input.required<number | undefined>();
  public documents = input.required<DocumentShortResponse[] | undefined>();

  public pageChange = output<number>();

  protected columns = ["Файл", "Статус", "Дата загрузки", "Авторы", "Тема", "Оценка", "Действия"];

  protected isLastPage = computed(() => {
    const total = this.total();
    return !total || this.page() * this.pageSize() >= total;
  });

  protected nextPage(): void {
    this.pageChange.emit(this.page() + 1);
  }

  protected prevPage(): void {
    this.pageChange.emit(this.page() - 1);
  }

  protected download(
    event: MouseEvent,
    documentId: string,
    filename: string,
  ): any {
    event.stopPropagation();

    return this.http.get(
      `${env.API_BASE_URL}documents/${documentId}/download`,
      { responseType: "blob" },
    ).pipe(
      tap((doc) => {
        const url = URL.createObjectURL(doc);

        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        a.click();

        URL.revokeObjectURL(url);
      }),
    ).subscribe();
  }
}
