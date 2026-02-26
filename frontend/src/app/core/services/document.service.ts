import { HttpClient, HttpEventType, HttpParams } from "@angular/common/http";
import { inject, Injectable } from "@angular/core";
import { map, Observable, startWith, Subject, switchMap, tap } from "rxjs";

import { env } from "../../../environments/environment";
import { DocumentResponse, DocumentShortResponse } from "../../features/documents/dto";
import { DocumentStatus } from "../../shared/enums";
import { FindManyApiResponse } from "../interfaces";

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
  ): Observable<FindManyApiResponse<DocumentShortResponse>> {
    return this.refresh$.pipe(
      startWith(void 0),
      switchMap(() => this.findMany({ limit })),
    );
  }

  public findById(
    id: string,
  ): Observable<DocumentResponse> {
    return this.http.get<DocumentResponse>(`${env.API_BASE_URL}documents/${id}`);
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

  public findMany(
    options: {
      limit?: number;
      offset?: number;
      status?: DocumentStatus;
      query?: string;
    },
  ): Observable<FindManyApiResponse<DocumentShortResponse>> {
    const { limit, offset, status, query } = options;

    const params = new HttpParams({
      fromObject: {
        limit: limit ?? 25,
        offset: offset ?? 0,
        ...(status && { status }),
        ...(query && { query }),
      },
    });

    return this.http.get<FindManyApiResponse<DocumentShortResponse>>(
      query ? `${env.API_BASE_URL}documents/search` : `${env.API_BASE_URL}documents`,
      { params },
    );
  }

  public download(
    documentId: string,
    filename?: string,
  ): Observable<any> {
    return this.http.get(
      `${env.API_BASE_URL}documents/${documentId}/download`,
      { responseType: "blob" },
    ).pipe(
      tap((doc) => {
        const url = URL.createObjectURL(doc);

        const a = document.createElement("a");
        a.href = url;
        if (filename)
          a.download = filename;
        a.click();

        URL.revokeObjectURL(url);
      }),
    );
  }
}
