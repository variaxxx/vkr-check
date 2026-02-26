import { Component } from "@angular/core";
import { RouterOutlet } from "@angular/router";

import { NotificationsStack } from "./shared/components/notifications-stack/notifications-stack";

@Component({
  selector: "app-root",
  imports: [RouterOutlet, NotificationsStack],
  template: "<router-outlet></router-outlet> <app-notifications-stack></app-notifications-stack>",
})
export class App {}
