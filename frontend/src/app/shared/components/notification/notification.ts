import { NgClass } from "@angular/common";
import { ChangeDetectionStrategy, Component, inject, input } from "@angular/core";

import { IconName } from "../../../app.icons";
import { NotificationItem, NotificationService, NotificationType } from "../../../core/services";
import { Icon } from "../icon/icon";

interface NotificationConfig {
  icon: IconName;
  title: string;
  classes: string;
}

const NOTIFICATION_CONFIG: Record<NotificationType, NotificationConfig> = {
  info: {
    icon: "info",
    title: "Информация",
    classes: "bg-blue-50 text-blue-600",
  },
  error: {
    icon: "alert-circle",
    title: "Ошибка",
    classes: "bg-red-50 text-red-600",
  },
  warning: {
    icon: "alert-triangle",
    title: "Предупреждение",
    classes: "bg-amber-50 text-amber-600",
  },
  success: {
    icon: "check-circle",
    title: "Успешно",
    classes: "bg-green-50 text-green-600",
  },
};

@Component({
  selector: "app-notification",
  imports: [Icon, NgClass],
  templateUrl: "./notification.html",
  styleUrl: "./notification.scss",
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Notification {
  notification = input.required<NotificationItem>();

  private readonly notificationService = inject(NotificationService);

  get config(): NotificationConfig {
    return NOTIFICATION_CONFIG[this.type];
  }

  get type(): NotificationType {
    return this.notification().type;
  }

  dismiss(): void {
    this.notificationService.dismiss(this.notification().id);
  }
}
