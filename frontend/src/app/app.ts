import { NotificationsStack } from "./shared/components/notifications-stack/notifications-stack";
import { Component } from "@angular/core";
import { RouterOutlet } from "@angular/router";

@Component({
  selector: "app-root",
  imports: [RouterOutlet, NotificationsStack],
  template: "<router-outlet></router-outlet> <app-notifications-stack></app-notifications-stack>",
})
export class App {}
