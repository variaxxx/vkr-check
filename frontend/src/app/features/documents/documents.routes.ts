import { Routes } from "@angular/router";

export const routes: Routes = [
  {
    path: "",
    loadComponent: () => import("./pages/history-page/history-page").then(m => m.HistoryPage),
  },
  {
    path: ":docId",
    loadComponent: () => import("./pages/document-page/document-page").then(m => m.DocumentPage),
  },
];

export default routes;
