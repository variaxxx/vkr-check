import { env } from "../../../environments/environment";
import { DocumentShortResponse } from "../../features/documents/dto";
import { DocumentStatus } from "../../shared/enums";
import { FindManyApiReponse } from "../interfaces";
import { HttpClient, HttpEventType, HttpParams } from "@angular/common/http";
import { inject, Injectable } from "@angular/core";
import { map, Observable, startWith, Subject, switchMap } from "rxjs";

export interface UploadingProgress {
  progress: number;
  done?: boolean;
  skippedFiles?: string[];
  skippedFilesCount?: number;
}

@Injectable({ providedIn: "root" })
export class DocumentService {
  private readonly http = inject(HttpClient);

  private refresh$ = new Subject<void>();

  public refreshDocuments(): void {
    this.refresh$.next();
  }

  public getRecent(
    limit: number = 5,
  ): Observable<FindManyApiReponse<DocumentShortResponse>> {
    return this.refresh$.pipe(
      startWith(void 0),
      switchMap(() => this.getMany({ limit })),
    );
  }

  public upload(docs: File[]): Observable<UploadingProgress> {
    const fd = new FormData();

    for (const file of docs) {
      fd.append("files", file);
    }

    return this.http.post<{
      skipped_count: number;
      skipped_files: string[];
    }>(
      `${env.API_BASE_URL}documents/upload`,
      fd,
      {
        reportProgress: true,
        observe: "events",
      },
    ).pipe(
      map((event) => {
        switch (event.type) {
          case HttpEventType.UploadProgress:
            return {
              progress: Math.round((event.loaded / (event.total || 1)) * 100),
            };
          case HttpEventType.Response:
            return { progress: 100, done: true, skippedFiles: event.body?.skipped_files, skippedFilesCount: event.body?.skipped_count };
          default:
            return { progress: 0 };
        }
      }),
    );
  }

  public getMany(
    options: {
      limit?: number;
      offset?: number;
      status?: DocumentStatus;
    },
  ): Observable<FindManyApiReponse<DocumentShortResponse>> {
    const { limit, offset, status } = options;

    const params = new HttpParams({
      fromObject: {
        limit: limit ?? 25,
        offset: offset ?? 0,
        ...(status && { status }),
      },
    });

    return this.http.get<FindManyApiReponse<DocumentShortResponse>>(
      `${env.API_BASE_URL}documents`,
      { params },
    );
  }
}
