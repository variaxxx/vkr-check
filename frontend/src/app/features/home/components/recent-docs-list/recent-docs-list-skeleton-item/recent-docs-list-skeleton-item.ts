import { ChangeDetectionStrategy, Component } from "@angular/core";
import { NgxSkeletonLoaderComponent } from "ngx-skeleton-loader";

@Component({
  selector: "app-recent-docs-list-skeleton-item",
  imports: [NgxSkeletonLoaderComponent],
  templateUrl: "./recent-docs-list-skeleton-item.html",
  styleUrl: "./recent-docs-list-skeleton-item.scss",
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RecentDocsListSkeletonItem {

}
