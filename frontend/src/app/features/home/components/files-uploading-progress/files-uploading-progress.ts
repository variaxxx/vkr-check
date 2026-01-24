import { ChangeDetectionStrategy, Component, input } from "@angular/core";

@Component({
  selector: "app-files-uploading-progress",
  imports: [],
  templateUrl: "./files-uploading-progress.html",
  styleUrl: "./files-uploading-progress.scss",
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FilesUploadingProgress {
  public uploadingProgress = input.required<number>();
}
