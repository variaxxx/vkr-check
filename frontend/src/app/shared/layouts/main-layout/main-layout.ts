import { ChangeDetectionStrategy, Component } from "@angular/core";
import { RouterOutlet } from "@angular/router";

import { Header } from "../../components/header/header";
import { Navbar } from "../../components/navbar/navbar";

@Component({
  selector: "app-main-layout",
  imports: [RouterOutlet, Header, Navbar],
  templateUrl: "./main-layout.html",
  styleUrl: "./main-layout.scss",
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MainLayout {}
