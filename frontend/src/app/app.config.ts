import { provideHttpClient, withInterceptors } from "@angular/common/http";
import { ApplicationConfig, ErrorHandler, inject, provideAppInitializer, provideBrowserGlobalErrorListeners } from "@angular/core";
import { MAT_DATE_LOCALE } from "@angular/material/core";
import { provideRouter } from "@angular/router";
import { authInterceptor, responseDataInterceptor } from "@core/interceptors/";
import { ErrorHandlerService } from "@core/services";
import { IconService } from "@shared/components/icon/icon.service";
import { provideNgxSkeletonLoader } from "ngx-skeleton-loader";
import { firstValueFrom } from "rxjs";

import { iconsConfig } from "./app.icons";
import { routes } from "./app.routes";

export function appInit() {
  const icon = inject(IconService);
  return firstValueFrom(icon.initIcons(iconsConfig));
}

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes),
    provideHttpClient(withInterceptors([authInterceptor, responseDataInterceptor])),
    provideAppInitializer(appInit),
    provideNgxSkeletonLoader({
      theme: {
        extendsFromRoot: true,
        display: "block",
      },
    }),
    { provide: ErrorHandler, useClass: ErrorHandlerService },
    { provide: MAT_DATE_LOCALE, useValue: "ru-RU" },
  ],
};
