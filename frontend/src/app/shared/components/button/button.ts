import { ChangeDetectionStrategy, Component, input } from "@angular/core";

import { ButtonPriority, ButtonSize, ButtonType } from "./button.types";

@Component({
  selector: "app-button",
  imports: [],
  templateUrl: "./button.html",
  styleUrl: "./button.scss",
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Button {
  type = input<ButtonType>("button");
  priority = input<ButtonPriority>("primary");
  size = input<ButtonSize>("md");
  disabled = input<boolean>(false);
}
