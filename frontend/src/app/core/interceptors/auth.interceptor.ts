import { HttpEvent, HttpHandlerFn, HttpRequest } from "@angular/common/http";
import { inject } from "@angular/core";
import { Router } from "@angular/router";
import { BehaviorSubject, catchError, filter, Observable, switchMap, tap, throwError } from "rxjs";

import { env } from "../../../environments/environment";
import { AuthService, NotificationService } from "../services";

const isRefreshing$ = new BehaviorSubject<boolean>(false);

export function authInterceptor(req: HttpRequest<unknown>, next: HttpHandlerFn): Observable<HttpEvent<any>> {
  const authService = inject(AuthService);
  const notificationService = inject(NotificationService);
  const token = authService.token;

  if (!token) {
    return next(req).pipe(
      catchError((err) => {
        if (err.status === 0) {
          notificationService.error("В данный момент сервер недоступен");
        } else if (err.status === 403) {
          notificationService.error("У Вас нет доступа");
        }

        return throwError(() => err);
      }),
    );
  }

  return next(addToken(req, token)).pipe(
    catchError((err) => {
      if (err.status === 401) {
        if (req.url.startsWith(env.API_BASE_URL) && req.url.includes("refresh"))
          return handleFailedRefresh(authService, err);
        return refreshAndProceed(authService, req, next);
      }

      if (err.status === 0) {
        notificationService.error("В данный момент сервер недоступен");
      } else if (err.status === 403) {
        notificationService.error("У Вас нет доступа");
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
