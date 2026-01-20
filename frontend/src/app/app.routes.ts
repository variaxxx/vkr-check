import { IsLoggedInGuard } from "./core/guards/auth.guard";
import { Routes } from "@angular/router";

export const routes: Routes = [
  {
    path: "auth",
    loadChildren: () => import("./features/auth/auth.routes"),
  },
  {
    path: "",
    loadComponent: () => import("./shared/layouts/main-layout/main-layout").then(m => m.MainLayout),
    canActivate: [IsLoggedInGuard],
    children: [
      {
        path: "",
        loadComponent: () => import("./features/home/home").then(m => m.Home),
      },
    ],
  },
];
