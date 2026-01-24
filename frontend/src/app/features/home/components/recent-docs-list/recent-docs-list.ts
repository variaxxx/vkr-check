import { DocumentService } from "../../../../core/services";
import { Icon } from "../../../../shared/components/icon/icon";
import { RecentDocsListItem } from "./recent-docs-list-item/recent-docs-list-item";
import { AsyncPipe } from "@angular/common";
import { ChangeDetectionStrategy, Component, inject } from "@angular/core";
import { RouterLink } from "@angular/router";

@Component({
  selector: "app-recent-docs-list",
  imports: [AsyncPipe, RecentDocsListItem, RouterLink, Icon],
  templateUrl: "./recent-docs-list.html",
  styleUrl: "./recent-docs-list.scss",
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RecentDocsList {
  private readonly docService = inject(DocumentService);

  protected recentDocuments$ = this.docService.getRecent();
}
