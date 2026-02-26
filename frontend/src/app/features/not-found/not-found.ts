import { ChangeDetectionStrategy, Component } from "@angular/core";
import { RouterLink } from "@angular/router";

import { Button } from "../../shared/components/button/button";

@Component({
  selector: "app-not-found",
  imports: [Button, RouterLink],
  templateUrl: "./not-found.html",
  styleUrl: "./not-found.scss",
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class NotFound {

}
