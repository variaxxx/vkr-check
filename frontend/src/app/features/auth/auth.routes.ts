import { Routes } from "@angular/router";

export const routes: Routes = [
  {
    path: "callback",
    loadComponent: () => import("./pages/auth-callback-page/auth-callback-page").then(m => m.AuthCallbackPage),
  },
  {
    path: "",
    loadComponent: () => import("./pages/auth-page/auth-page").then(m => m.AuthPage),
  },
];

export default routes;
