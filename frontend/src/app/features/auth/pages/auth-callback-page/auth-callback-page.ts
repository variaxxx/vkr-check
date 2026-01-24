import { AuthService } from "../../../../core/services";
import { ChangeDetectionStrategy, Component, DestroyRef, inject, OnInit } from "@angular/core";
import { takeUntilDestroyed } from "@angular/core/rxjs-interop";
import { ActivatedRoute, Router } from "@angular/router";
import { map, switchMap } from "rxjs";

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
      map((frag) => {
        if (frag === null)
          throw new Error("No fragment");

        const params = new URLSearchParams(frag!);

        const token = params.get("access_token");
        if (!token)
          throw new Error("No token");

        const receivedState = params.get("state");
        const storedState = sessionStorage.getItem("authState");
        if (receivedState !== storedState)
          throw new Error("Invalid state");

        const idToken = params.get("id_token");
        if (!idToken)
          throw new Error("No token ID");
        const payload = idToken.split(".")[1];
        const jsonPayload = JSON.parse(atob(payload));
        const receivedNonce = jsonPayload.nonce;
        const storedNonce = sessionStorage.getItem("authNonce");
        if (!receivedNonce || receivedNonce !== storedNonce)
          throw new Error("Invalid nonce");

        return token;
      }),
      switchMap(token => this.authService.login(token!)),
    ).subscribe({
      next: () => this.router.navigateByUrl("/"),
      error: (err) => {
        console.error(`Authorization failed: ${err}`);
        this.router.navigateByUrl("/auth");
      },
    });
  }
}
