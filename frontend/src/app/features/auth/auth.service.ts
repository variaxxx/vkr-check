import { Injectable } from "@angular/core";

@Injectable({
  providedIn: "root",
})
export class AuthService {
  private _token: string | null = localStorage.getItem("accessToken");

  public login(token: string): void {
    localStorage.setItem("accessToken", token);
    this._token = token;
  }

  public isLoggedIn(): boolean {
    return !!this.token;
  }

  get token(): string | null {
    return this._token;
  }
}
