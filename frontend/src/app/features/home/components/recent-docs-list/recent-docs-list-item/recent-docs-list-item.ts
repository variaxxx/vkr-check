import { IconName } from "../../../../../app.icons";
import { Icon } from "../../../../../shared/components/icon/icon";
import { DOCUMENT_STATUS, DocumentStatus } from "../../../../../shared/enums";
import { PrettyDatePipe } from "../../../../../shared/pipes";
import { DocumentInfoResponse } from "../../../../documents/dto";
import { NgClass } from "@angular/common";
import { ChangeDetectionStrategy, Component, input } from "@angular/core";

interface StatusConfig {
  icon: IconName;
  label: string;
  classes: string;
}

const STATUS_CONFIG: Record<DocumentStatus, StatusConfig> = {
  [DOCUMENT_STATUS.UPLOADED]: {
    icon: "upload",
    label: "Загружен",
    classes: "text-neutral-600 bg-neutral-100",
  },
  [DOCUMENT_STATUS.IN_PROCESSING]: {
    icon: "clock",
    label: "В обработке",
    classes: "text-blue-600 bg-blue-100",
  },
  [DOCUMENT_STATUS.FAILED]: {
    icon: "alert-circle",
    label: "Ошибка",
    classes: "text-red-600 bg-red-100",
  },
  [DOCUMENT_STATUS.SUCCESS]: {
    icon: "check-circle",
    label: "Успешно",
    classes: "text-green-600 bg-green-100",
  },
};

@Component({
  selector: "app-recent-docs-list-item",
  imports: [Icon, NgClass, PrettyDatePipe],
  templateUrl: "./recent-docs-list-item.html",
  styleUrl: "./recent-docs-list-item.scss",
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RecentDocsListItem {
  doc = input.required<DocumentInfoResponse>();

  get status(): StatusConfig {
    return STATUS_CONFIG[this.doc().status];
  }
}
