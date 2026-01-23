import { DocumentService } from "../../core/services";
import { FilesInput } from "./components/files-input/files-input";
import { FilesList } from "./components/files-list/files-list";
import { RecentDocsList } from "./components/recent-docs-list/recent-docs-list";
import { ChangeDetectionStrategy, Component, DestroyRef, inject, signal } from "@angular/core";
import { takeUntilDestroyed } from "@angular/core/rxjs-interop";
import { FormControl, FormGroup, ReactiveFormsModule } from "@angular/forms";

@Component({
  selector: "app-home",
  imports: [
    FilesInput,
    FilesList,
    ReactiveFormsModule,
    RecentDocsList,
  ],
  templateUrl: "./home.html",
  styleUrl: "./home.scss",
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Home {
  private readonly docsService = inject(DocumentService);
  private readonly destroyRef = inject(DestroyRef);

  form = new FormGroup({
    files: new FormControl<File[]>([], { nonNullable: true }),
  });

  isUploading = signal<boolean>(false);
  uploadingProgress = signal<number>(0);

  submit(): void {
    if (this.isUploading())
      // TODO: notification
      return;

    this.isUploading.set(true);
    this.docsService.upload(this.form.controls.files.value).pipe(
      takeUntilDestroyed(this.destroyRef),
    ).subscribe({
      next: (event) => {
        this.uploadingProgress.set(event.progress);
        if (event.done) {
          this.uploadingProgress.set(0);
          this.isUploading.set(false);
          setTimeout(() => this.form.controls.files.setValue([]), 1000);
          // TODO: update recent docs
        }
      },
      error: (err) => {
        // TODO: notification
        console.error(err);
      },
    });
  }
}
