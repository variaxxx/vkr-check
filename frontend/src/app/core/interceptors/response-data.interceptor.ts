import { env } from "../../../environments/environment";
import { ApiResponse } from "../interfaces";
import { HttpEvent, HttpHandlerFn, HttpRequest, HttpResponse } from "@angular/common/http";
import { map, Observable } from "rxjs";

export function responseDataInterceptor(req: HttpRequest<unknown>, next: HttpHandlerFn): Observable<HttpEvent<any>> {
  return next(req).pipe(
    map((event) => {
      if (event instanceof HttpResponse && event.url?.startsWith(env.API_BASE_URL)) {
        const body = event.body as ApiResponse;
        return event.clone({ body: body.data });
      }
      return event;
    }),
  );
}
