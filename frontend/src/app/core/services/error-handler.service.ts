import { ErrorHandler, inject, Injectable } from "@angular/core";

import { NotificationService } from "./notification.service";

@Injectable()
export class ErrorHandlerService implements ErrorHandler {
  private readonly notificationService = inject(NotificationService);

  handleError(error: any): void {
    this.notificationService.error("Что-то пошло не так");
    console.error(ErrorHandlerService.name, { error });
  }
}
