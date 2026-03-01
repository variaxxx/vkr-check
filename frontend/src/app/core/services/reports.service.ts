import { HttpClient, HttpParams } from "@angular/common/http";
import { inject, Injectable } from "@angular/core";
import { Observable } from "rxjs";

import { env } from "../../../environments/environment";

@Injectable({ providedIn: "root" })
export class ReportsService {
  private readonly http = inject(HttpClient);

  public downloadForAll(
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
    );
  }

  public downloadForDoc(
    docId: string,
  ): Observable<any> {
    return this.http.get(
      `${env.API_BASE_URL}documents/${docId}/report`,
      { responseType: "blob" },
    );
  }
}
