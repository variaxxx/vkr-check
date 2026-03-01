import { ChangeDetectionStrategy, Component, DestroyRef, inject, signal } from "@angular/core";
import { takeUntilDestroyed } from "@angular/core/rxjs-interop";
import { FormControl, FormGroup, ReactiveFormsModule } from "@angular/forms";

import { DocumentService, NotificationService } from "../../core/services";
import { FilesInput } from "./components/files-input/files-input";
import { FilesList } from "./components/files-list/files-list";
import { FilesUploadingProgress } from "./components/files-uploading-progress/files-uploading-progress";
import { RecentDocsList } from "./components/recent-docs-list/recent-docs-list";

@Component({
  selector: "app-home",
  imports: [
    FilesInput,
    FilesList,
    ReactiveFormsModule,
    RecentDocsList,
    FilesUploadingProgress,
  ],
  templateUrl: "./home.html",
  styleUrl: "./home.scss",
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Home {
  private readonly docsService = inject(DocumentService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly notificationService = inject(NotificationService);

  form = new FormGroup({
    files: new FormControl<File[]>([], { nonNullable: true }),
  });

  isUploading = signal<boolean>(false);
  uploadingProgress = signal<number>(0);

  submit(): void {
    if (this.isUploading())
      return this.notificationService.warn("Вы уже загружаете документы");

    this.isUploading.set(true);
    this.docsService.upload(this.form.controls.files.value).pipe(
      takeUntilDestroyed(this.destroyRef),
    ).subscribe({
      next: (event) => {
        this.uploadingProgress.set(event.progress);

        if (event.done) {
          this.uploadingProgress.set(0);
          this.isUploading.set(false);
          this.form.controls.files.setValue([]);

          this.notificationService.success("Документы успешно загружены");

          this.docsService.refreshDocuments();
        }
      },
      error: (err) => {
        this.notificationService.error("Что-то пошло не так при загрузке документов");
        console.error(err);
      },
    });
  }
}
