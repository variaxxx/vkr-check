import { IsLoggedInGuard } from "./core/guards/is-logged-in.guard";
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
      {
        path: "history",
        loadComponent: () => import("./features/history/history").then(m => m.History),
      },
    ],
  },
  {
    path: "**",
    loadComponent: () => import("./features/not-found/not-found").then(m => m.NotFound),
  },
];
