import { ChangeDetectionStrategy, Component } from "@angular/core";
import { RouterLink, RouterLinkActive } from "@angular/router";

import { IconName } from "../../../app.icons";
import { Icon } from "../icon/icon";

export interface AppRoute {
  route: string;
  label: string;
  icon: IconName;
}

@Component({
  selector: "app-navbar",
  imports: [Icon, RouterLink, RouterLinkActive],
  templateUrl: "./navbar.html",
  styleUrl: "./navbar.scss",
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Navbar {
  public routes: AppRoute[] = [
    {
      route: "",
      label: "Загрузка",
      icon: "upload",
    },
    {
      route: "documents/",
      label: "История",
      icon: "history",
    },
    {
      route: "reports/",
      label: "Отчёты",
      icon: "document",
    },
  ];
}
