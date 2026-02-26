import { inject } from "@angular/core";
import {
  ActivatedRouteSnapshot,
  CanActivateFn,
  Router,
  RouterStateSnapshot,
} from "@angular/router";
import { map } from "rxjs";

import { AuthService } from "../services";

export const IsLoggedInGuard: CanActivateFn = (
  route: ActivatedRouteSnapshot,
  state: RouterStateSnapshot,
) => {
  const router = inject(Router);
  const auth = inject(AuthService);

  return auth.isLoggedIn$().pipe(
    map((val) => {
      if (!val)
        return router.parseUrl("/auth");
      return true;
    }),
  );
};
