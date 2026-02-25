import { Observable } from 'rxjs';

import { HttpResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';

import { BaseService } from '../base-service/base.service';
import { ApiResponseCollection } from '../api-response-interface';
import {
    BatchError,
    BatchErrorCollectionPaginationParams,
    BatchErrorCountsParams,
    BatchErrorExportParams,
} from './batch-error-interface';

@Injectable({
    providedIn: 'root',
})
export class BatchErrorService extends BaseService {
    apiUrl: string = '/api/report/batch-error';

    getCollection(params: BatchErrorCollectionPaginationParams): Observable<any> {
        return this.http.get<ApiResponseCollection<BatchError>>(`${this.apiUrl}`, {
            params: this.convertToHttpParams(params),
        });
    }

    getCounts(
        params: BatchErrorCountsParams,
    ): Observable<{ data: { count: number; error: string; code: string }[] }> {
        return this.http.get<{ data: { count: number; error: string; code: string }[] }>(
            '/api/report/batch-error-counts',
            {
                params: this.convertToHttpParams(params),
            },
        );
    }

    export(params: BatchErrorExportParams): Observable<HttpResponse<Blob>> {
        const httpParams = this.convertToHttpParams(params);
        return this.http.get(`${this.apiUrl}/export`, {
            params: httpParams,
            responseType: 'blob',
            observe: 'response',
        });
    }
}
