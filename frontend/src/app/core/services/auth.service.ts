import { env } from "../../../environments/environment";
import { AccessTokenResponse, UserInfoResponse } from "../../features/auth/dto";
import { randomString } from "../../shared/utils";
import { HttpClient } from "@angular/common/http";
import { inject, Injectable } from "@angular/core";
import { BehaviorSubject, catchError, map, Observable, of, tap } from "rxjs";

@Injectable({
  providedIn: "root",
})
export class AuthService {
  private _token?: string;
  private _isLoggedIn$ = new BehaviorSubject<boolean | null>(null);
  private _me$ = new BehaviorSubject<UserInfoResponse | null>(null);

  private readonly http = inject(HttpClient);

  public login(kcToken: string): Observable<AccessTokenResponse> {
    return this.http.post<AccessTokenResponse>(
      `${env.API_BASE_URL}auth/kc`,
      { token: kcToken },
      { withCredentials: true },
    ).pipe(
      tap((res) => {
        this._token = res.access_token;
        this._isLoggedIn$.next(true);
      }),
    );
  }

  public logout(): Observable<null> {
    return this.http.post<null>(
      `${env.API_BASE_URL}auth/logout`,
      {},
      { withCredentials: true },
    ).pipe(
      tap(() => {
        this._token = undefined;
        this._isLoggedIn$.next(false);
        this._me$.next(null);
      }),
    );
  }

  public refreshToken(): Observable<AccessTokenResponse> {
    return this.http.post<AccessTokenResponse>(
      `${env.API_BASE_URL}auth/refresh`,
      {},
      { withCredentials: true },
    ).pipe(
      tap((res) => {
        this._token = res.access_token;
        this._isLoggedIn$.next(true);
      }),
    );
  }

  public getMe$(): Observable<UserInfoResponse> {
    if (this._me$.value === null) {
      return this.http.get<UserInfoResponse>(
        `${env.API_BASE_URL}user/me`,
      ).pipe(
        tap((res) => {
          this._me$.next(res);
        }),
      );
    }
    return of(this._me$.value);
  }

  public isLoggedIn$(): Observable<boolean> {
    if (this._isLoggedIn$.value === null) {
      return this.refreshToken().pipe(
        map(() => this._isLoggedIn$.value as boolean),
        catchError(() => of(false)),
      );
    }

    return of(this._isLoggedIn$.value);
  }

  public genAuthLink(): string {
    const state = randomString();
    sessionStorage.setItem("authState", state);

    const nonce = randomString();
    sessionStorage.setItem("authNonce", nonce);

    const searchParams = new URLSearchParams({
      response_type: "id_token token",
      client_id: env.KEYCLOAK_CLIENT_ID,
      redirect_uri: `${env.HOST}auth/callback`,
      scope: "openid profile",
      state,
      nonce,
    });

    return `${env.KEYCLOAK_BASE_URL}${env.KEYCLOACK_USES_AUTH_ENDPOINT ? "auth/" : ""}realms/${env.KEYCLOAK_REALM}/protocol/openid-connect/auth?${searchParams.toString()}`;
  }

  get token(): string | undefined {
    return this._token;
  }
}
