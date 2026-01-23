import { Icon } from "../../../../../shared/components/icon/icon";
import { FileSizePipe } from "../../../../../shared/pipes";
import { ChangeDetectionStrategy, Component, input, output } from "@angular/core";

@Component({
  selector: "app-files-list-item",
  imports: [Icon, FileSizePipe],
  templateUrl: "./files-list-item.html",
  styleUrl: "./files-list-item.scss",
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FilesListItem {
  file = input.required<File>();

  removeOutput = output<File>({ alias: "remove" });

  remove(): void {
    this.removeOutput.emit(this.file());
  }
}
