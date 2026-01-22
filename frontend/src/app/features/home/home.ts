import { env } from "../../../environments/environment";
import { AsyncPipe, JsonPipe } from "@angular/common";
import { HttpClient } from "@angular/common/http";
import { ChangeDetectionStrategy, Component, inject } from "@angular/core";

@Component({
  selector: "app-home",
  imports: [
    AsyncPipe,
    JsonPipe,
  ],
  templateUrl: "./home.html",
  styleUrl: "./home.scss",
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Home {
  private readonly http = inject(HttpClient);

  protected documents$ = this.http.get<object>(`${env.API_BASE_URL}documents`).pipe();
}
