import { Injectable, signal } from "@angular/core";
import { toObservable } from "@angular/core/rxjs-interop";

export type NotificationType = "info" | "warning" | "error" | "success";

export interface NotificationItem {
  id: number;
  type: NotificationType;
  message: string;
  timeoutMs?: number;
}

@Injectable({ providedIn: "root" })
export class NotificationService {
  private counter = 0;
  private notifications = signal<NotificationItem[]>([]);
  readonly notifications$ = toObservable(this.notifications);

  public info(message: string, timeout?: number): void {
    this.show("info", message, timeout);
  }

  public warn(message: string, timeout: number = 3000): void {
    this.show("warning", message, timeout);
  }

  public error(message: string, timeout: number = 5000): void {
    this.show("error", message, timeout);
  }

  public success(message: string, timeout: number = 15000): void {
    this.show("success", message, timeout);
  }

  private show(
    type: NotificationType,
    message: string,
    timer?: number,
  ): void {
    const id = ++this.counter;
    const notification: NotificationItem = {
      id,
      type,
      message,
      timeoutMs: timer,
    };

    this.notifications.set([...this.notifications(), notification]);

    if (timer) {
      setTimeout(() => this.dismiss(id), timer);
    }
  }

  public dismiss(
    id: number,
  ): void {
    this.notifications.set(
      this.notifications()
        .filter(i => i.id !== id),
    );
  }
}
