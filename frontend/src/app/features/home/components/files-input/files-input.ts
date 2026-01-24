import { NotificationService } from "../../../../core/services";
import { Button } from "../../../../shared/components/button/button";
import { Icon } from "../../../../shared/components/icon/icon";
import { NgClass } from "@angular/common";
import { ChangeDetectionStrategy, Component, ElementRef, forwardRef, inject, input, signal, ViewChild } from "@angular/core";
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from "@angular/forms";

@Component({
  selector: "app-files-input",
  imports: [Icon, Button, NgClass],
  templateUrl: "./files-input.html",
  styleUrl: "./files-input.scss",
  changeDetection: ChangeDetectionStrategy.OnPush,
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => FilesInput),
      multi: true,
    },
  ],
})
export class FilesInput implements ControlValueAccessor {
  private readonly notificationService = inject(NotificationService);

  private ALLOWED_FILE_TYPES = [
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/pdf",
  ];

  isUploading = input<boolean>(false);

  protected isDraggedOver = signal<boolean>(false);
  protected files = signal<File[]>([]);

  @ViewChild("fileInput") fileInput!: ElementRef<HTMLInputElement>;

  triggerFileSelect(): void {
    this.fileInput.nativeElement.click();
  }

  onFileChange(event: Event): void {
    const target = event.target as HTMLInputElement;

    if (!target || !target.files?.length)
      return;

    this.processFiles(target.files);
  };

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    // event.dataTransfer!.dropEffect = "copy";
    this.isDraggedOver.set(true);
  }

  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    this.isDraggedOver.set(false);
  }

  onFileDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();

    this.isDraggedOver.set(false);

    if (!event.dataTransfer?.files.length)
      return;

    this.processFiles(event.dataTransfer.files);
  }

  remove(name: string): void {
    this.files.set(this.files().filter(i => i.name !== name));
  }

  private processFiles(files: File[] | FileList): void {
    if (this.isUploading())
      return this.notificationService.warn("Вы не можете добавлять файлы во время загрузки");

    const updates: File[] = [];

    for (const file of files) {
      if (!this.ALLOWED_FILE_TYPES.includes(file.type))
        return this.notificationService.error("Данный тип файла не поддерживается");

      updates.push(file);
    }

    this.files.set([...this.files(), ...updates]);
    this.onChange(this.files());
    this.onTouched();
  }

  writeValue(obj: File[]): void {
    this.files.set(obj);
  }

  registerOnChange(fn: any): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: any): void {
    this.onTouched = fn;
  }

  onChange = (value: any): void => {};
  onTouched = (): void => {};
}
