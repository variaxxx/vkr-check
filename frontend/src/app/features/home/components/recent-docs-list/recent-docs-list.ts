import { ChangeDetectionStrategy, Component, DestroyRef, inject, OnInit, signal } from "@angular/core";
import { takeUntilDestroyed } from "@angular/core/rxjs-interop";
import { RouterLink } from "@angular/router";
import { tap } from "rxjs";

import { FindManyApiResponse } from "../../../../core/interfaces";
import { DocumentService } from "../../../../core/services";
import { Icon } from "../../../../shared/components/icon/icon";
import { DocumentShortResponse } from "../../../documents/dto";
import { RecentDocsListItem } from "./recent-docs-list-item/recent-docs-list-item";
import { RecentDocsListSkeletonItem } from "./recent-docs-list-skeleton-item/recent-docs-list-skeleton-item";

@Component({
  selector: "app-recent-docs-list",
  imports: [RecentDocsListItem, RouterLink, Icon, RecentDocsListSkeletonItem],
  templateUrl: "./recent-docs-list.html",
  styleUrl: "./recent-docs-list.scss",
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RecentDocsList implements OnInit {
  private readonly docService = inject(DocumentService);
  private readonly destroyRef = inject(DestroyRef);

  protected docsState = signal<{
    data: FindManyApiResponse<DocumentShortResponse> | null;
    isLoading: boolean;
  }>({
    data: null,
    isLoading: false,
  });

  ngOnInit(): void {
    this.getRecentDocs();
  }

  public getRecentDocs(): void {
    this.docsState.update(state => ({ ...state, isLoading: true }));

    this.docService.getRecent().pipe(
      takeUntilDestroyed(this.destroyRef),
      tap((data) => {
        this.docsState.set({
          data,
          isLoading: false,
        });
      }),
    ).subscribe();
  }
}
