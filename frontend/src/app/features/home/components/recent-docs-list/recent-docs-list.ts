import { FindManyApiReponse } from "../../../../core/interfaces";
import { DocumentService } from "../../../../core/services";
import { Icon } from "../../../../shared/components/icon/icon";
import { DOCUMENT_STATUS } from "../../../../shared/enums";
import { DocumentInfoResponse } from "../../../documents/dto";
import { RecentDocsListItem } from "./recent-docs-list-item/recent-docs-list-item";
import { AsyncPipe } from "@angular/common";
import { ChangeDetectionStrategy, Component, inject } from "@angular/core";
import { RouterLink } from "@angular/router";
import { of } from "rxjs";

const mockDocs: FindManyApiReponse<DocumentInfoResponse> = {
  total: 10,
  count: 4,
  items: [
    {
      id: "1",
      created_at: new Date(),
      original_name: "VKR1.docx",
      status: DOCUMENT_STATUS.UPLOADED,
    },
    {
      id: "2",
      created_at: new Date(),
      original_name: "VKR2.docx",
      status: DOCUMENT_STATUS.FAILED,
    },
    {
      id: "3",
      created_at: new Date(),
      original_name: "VKR3.docx",
      status: DOCUMENT_STATUS.IN_PROCESSING,
    },
    {
      id: "4",
      created_at: new Date(),
      original_name: "VKR4.pdf",
      status: DOCUMENT_STATUS.SUCCESS,
      processed_at: new Date(),
      authors: [
        "Пупкин Иван Сергеевич",
      ],
      result: "smth",
    },
  ],
};

@Component({
  selector: "app-recent-docs-list",
  imports: [AsyncPipe, RecentDocsListItem, RouterLink, Icon],
  templateUrl: "./recent-docs-list.html",
  styleUrl: "./recent-docs-list.scss",
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RecentDocsList {
  private readonly docService = inject(DocumentService);

  // recentDocuments$ = this.docService.getMany(5, 0);
  recentDocuments$ = of(mockDocs);
  // recentDocuments$ = of({ items: [], total: 10, count: 0 } as FindManyApiReponse<DocumentInfoResponse>);
}
