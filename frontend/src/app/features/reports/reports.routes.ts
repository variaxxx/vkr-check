import { Routes } from "@angular/router";

export const routes: Routes = [
  {
    path: "",
    loadComponent: () => import("./pages/report-page/report-page").then(m => m.ReportPage),
  },
];

export default routes;
