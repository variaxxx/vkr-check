import { AsyncPipe } from "@angular/common";
import { ChangeDetectionStrategy, Component, input, OnInit, output } from "@angular/core";
import { FormControl } from "@angular/forms";
import { Observable, startWith } from "rxjs";

import { Button } from "../../../../shared/components/button/button";
import { Icon } from "../../../../shared/components/icon/icon";
import { FilesListItem } from "./files-list-item/files-list-item";

@Component({
  selector: "app-files-list",
  imports: [Button, Icon, FilesListItem, AsyncPipe],
  templateUrl: "./files-list.html",
  styleUrl: "./files-list.scss",
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FilesList implements OnInit {
  control = input.required<FormControl<File[]>>();
  isUploading = input<boolean>(false);
  uploadingProgress = input<number>(0);

  submitEvent = output({ alias: "submit" });

  files$?: Observable<File[]>;

  ngOnInit(): void {
    this.files$ = this.control().valueChanges.pipe(
      startWith(this.control().value ?? []),
    );
  }

  clearAll(): void {
    if (this.isUploading())
      return;
    this.control().setValue([]);
  }

  remove(file: File): void {
    if (this.isUploading())
      return;
    this.control().setValue(
      this.control().value.filter(f => f !== file),
    );
  }

  submit(): void {
    this.submitEvent.emit();
  }
}
