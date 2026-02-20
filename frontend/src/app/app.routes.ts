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
        path: "history",
        loadComponent: () => import("./features/documents/pages/history-page/history-page").then(m => m.HistoryPage),
      },
      {
        path: "docs/:docId",
        loadComponent: () => import("./features/documents/pages/document-page/document-page").then(m => m.DocumentPage),
      },
    ],
  },
  {
    path: "**",
    loadComponent: () => import("./features/not-found/not-found").then(m => m.NotFound),
  },
];
