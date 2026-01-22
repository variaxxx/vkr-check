import { env } from "../../../environments/environment";
import { AuthService } from "../services";
import { HttpEvent, HttpHandlerFn, HttpRequest } from "@angular/common/http";
import { inject } from "@angular/core";
import { Router } from "@angular/router";
import { BehaviorSubject, catchError, filter, Observable, switchMap, tap, throwError } from "rxjs";

const isRefreshing$ = new BehaviorSubject<boolean>(false);

export function authInterceptor(req: HttpRequest<unknown>, next: HttpHandlerFn): Observable<HttpEvent<any>> {
  const authService = inject(AuthService);
  const token = authService.token;

  if (!token)
    return next(req);

  return next(addToken(req, token)).pipe(
    catchError((err) => {
      if (err.status === 401) {
        if (req.url.startsWith(env.API_BASE_URL) && req.url.includes("refresh"))
          return handleFailedRefresh(authService, err);
        return refreshAndProceed(authService, req, next);
      }

      return throwError(() => err);
    }),
  );
}

function refreshAndProceed(authService: AuthService, req: HttpRequest<unknown>, next: HttpHandlerFn): Observable<HttpEvent<any>> {
  if (!isRefreshing$.value) {
    isRefreshing$.next(true);

    return authService.refreshToken().pipe(
      switchMap(val => next(addToken(req, val.access_token))),
      catchError(err => handleFailedRefresh(authService, err)),
    );
  }

  if (req.url.startsWith(env.API_BASE_URL) && req.url.includes("refresh"))
    return next(req);

  return isRefreshing$.pipe(
    filter(val => !val),
    switchMap(() => next(addToken(req, authService.token!))),
  );
}

function addToken(req: HttpRequest<any>, token: string): HttpRequest<any> {
  return req.clone({
    setHeaders: {
      Authorization: `Bearer ${token}`,
    },
  });
}

function handleFailedRefresh(authService: AuthService, err: any): Observable<any> {
  if (err.status === 401) {
    return authService.logout().pipe(
      tap(() => {
        inject(Router).navigateByUrl("/auth");
      }),
    );
  }

  isRefreshing$.next(false);
  return throwError(() => err);
}
