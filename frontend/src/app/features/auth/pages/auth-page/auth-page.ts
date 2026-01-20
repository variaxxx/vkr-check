import { env } from "../../../../../environments/environment";
import { AuthService } from "../../auth.service";
import { ChangeDetectionStrategy, Component, inject } from "@angular/core";

@Component({
  selector: "app-auth-page",
  templateUrl: "./auth-page.html",
  styleUrl: "./auth-page.scss",
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AuthPage {
  private readonly authService = inject(AuthService);

  get authLink(): string {
    const searchParams = new URLSearchParams();

    // TODO: support for old kk versions
    searchParams.append("response_type", "id_token token");
    searchParams.append("client_id", env.KEYCLOAK_CLIENT_ID);
    searchParams.append("redirect_uri", `${env.HOST}auth/callback`);
    searchParams.append("scope", "openid profile");
    searchParams.append("state", "local");
    // TODO: gen nonce & challenge
    searchParams.append("nonce", "rand123");
    searchParams.append("code_challenge", "9DNJSIcSs4mR1cyzPuZslCWRNq5y2rA_wPejSEIqV0c");
    searchParams.append("code_challenge_method", "S256");

    return `${env.KEYCLOAK_BASE_URL}realms/${env.KEYCLOAK_REALM}/protocol/openid-connect/auth?${searchParams.toString()}`;
  }
}
