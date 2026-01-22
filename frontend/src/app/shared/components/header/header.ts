import { AuthService } from "../../../core/services";
import { Button } from "../button/button";
import { Icon } from "../icon/icon";
import { AsyncPipe } from "@angular/common";
import { ChangeDetectionStrategy, Component, DestroyRef, inject } from "@angular/core";
import { takeUntilDestroyed } from "@angular/core/rxjs-interop";
import { Router } from "@angular/router";
import { tap } from "rxjs";

@Component({
  selector: "app-header",
  imports: [Button, Icon, AsyncPipe],
  templateUrl: "./header.html",
  styleUrl: "./header.scss",
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Header {
  private readonly authService = inject(AuthService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly router = inject(Router);

  public logout(): void {
    this.authService.logout().pipe(
      takeUntilDestroyed(this.destroyRef),
      tap(() => {
        this.router.navigateByUrl("/auth");
      }),
    ).subscribe();
  }

  public me$ = this.authService.getMe$();
}
