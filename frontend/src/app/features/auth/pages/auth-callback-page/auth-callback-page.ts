import { AuthService } from "../../auth.service";
import { ChangeDetectionStrategy, Component, DestroyRef, inject, OnInit } from "@angular/core";
import { takeUntilDestroyed } from "@angular/core/rxjs-interop";
import { ActivatedRoute, Router } from "@angular/router";

@Component({
  selector: "app-auth-callback-page",
  imports: [],
  template: "",
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AuthCallbackPage implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly destroyRef = inject(DestroyRef);
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  ngOnInit(): void {
    this.route.fragment.pipe(
      takeUntilDestroyed(this.destroyRef),
    ).subscribe((frag) => {
      if (frag === null)
        return;
      const params = new URLSearchParams(frag);
      const token = params.get("access_token");
      if (!token)
        return;
      this.authService.login(token);
      this.router.navigateByUrl("");
    });
  }
}
