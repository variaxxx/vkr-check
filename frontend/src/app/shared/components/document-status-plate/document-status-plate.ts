import { NgClass } from "@angular/common";
import { ChangeDetectionStrategy, Component, input } from "@angular/core";

import { IconName } from "../../../app.icons";
import { DOCUMENT_STATUS, DocumentStatus } from "../../enums";
import { Icon } from "../icon/icon";

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
  [DOCUMENT_STATUS.APPROVED]: {
    icon: "check-circle",
    label: "Зачёт",
    classes: "text-green-600 bg-green-100",
  },
  [DOCUMENT_STATUS.REJECTED]: {
    icon: "x-circle",
    label: "Незачёт",
    classes: "text-red-600 bg-red-100",
  },
};

@Component({
  selector: "app-document-status-plate",
  imports: [Icon, NgClass],
  templateUrl: "./document-status-plate.html",
  styleUrl: "./document-status-plate.scss",
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DocumentStatusPlate {
  public status = input.required<DocumentStatus>();

  get config(): StatusConfig {
    return STATUS_CONFIG[this.status()];
  }
}
