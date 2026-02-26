import { HttpClient, HttpParams } from "@angular/common/http";
import { inject, Injectable } from "@angular/core";
import { Observable, tap } from "rxjs";

import { env } from "../../../environments/environment";

@Injectable({ providedIn: "root" })
export class ReportsService {
  private readonly http = inject(HttpClient);

  public download(
    opts: {
      start: Date;
      end: Date;
    },
  ): Observable<any> {
    const params = new HttpParams({
      fromObject: {
        start: opts.start.toISOString(),
        end: opts.end.toISOString(),
      },
    });

    return this.http.get(
      `${env.API_BASE_URL}report`,
      { responseType: "blob", params },
    ).pipe(
      tap((report) => {
        const url = URL.createObjectURL(report);

        const a = document.createElement("a");
        a.href = url;
        a.download = "report.xlsx";
        a.click();

        URL.revokeObjectURL(url);
      }),
    );
  }
}
