import { AuthService } from "../../../../core/services";
import { Button } from "../../../../shared/components/button/button";
import { Icon } from "../../../../shared/components/icon/icon";
import { ChangeDetectionStrategy, Component, inject } from "@angular/core";

@Component({
  selector: "app-auth-page",
  templateUrl: "./auth-page.html",
  styleUrl: "./auth-page.scss",
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [Button, Icon],
})
export class AuthPage {
  private readonly authService = inject(AuthService);

  public login(): void {
    window.location.href = this.authService.genAuthLink();
  }
}
