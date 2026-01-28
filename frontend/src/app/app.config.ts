import { iconsConfig } from "./app.icons";
import { routes } from "./app.routes";
import { authInterceptor, responseDataInterceptor } from "./core/interceptors/";
import { IconService } from "./shared/components/icon/icon.service";
import { provideHttpClient, withInterceptors } from "@angular/common/http";
import { ApplicationConfig, inject, provideAppInitializer, provideBrowserGlobalErrorListeners } from "@angular/core";
import { provideRouter } from "@angular/router";
import { provideNgxSkeletonLoader } from "ngx-skeleton-loader";
import { firstValueFrom } from "rxjs";

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
  ],
};
