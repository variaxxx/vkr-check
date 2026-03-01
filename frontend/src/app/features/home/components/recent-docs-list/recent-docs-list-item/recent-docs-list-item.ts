import { ChangeDetectionStrategy, Component, input } from "@angular/core";

import { DocumentStatusPlate } from "../../../../../shared/components/document-status-plate/document-status-plate";
import { PrettyDatePipe } from "../../../../../shared/pipes";
import { DocumentShortResponse } from "../../../../documents/dto";

@Component({
  selector: "app-recent-docs-list-item",
  imports: [PrettyDatePipe, DocumentStatusPlate],
  templateUrl: "./recent-docs-list-item.html",
  styleUrl: "./recent-docs-list-item.scss",
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RecentDocsListItem {
  doc = input.required<DocumentShortResponse>();
}
