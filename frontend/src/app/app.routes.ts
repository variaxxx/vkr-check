import { Routes } from "@angular/router";

import { IsLoggedInGuard } from "./core/guards/is-logged-in.guard";

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
        path: "documents",
        loadChildren: () => import("./features/documents/documents.routes"),
      },
      {
        path: "reports",
        loadChildren: () => import("./features/reports/reports.routes"),
      },
    ],
  },
  {
    path: "**",
    loadComponent: () => import("./features/not-found/not-found").then(m => m.NotFound),
  },
];
