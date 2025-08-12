import { Observable } from 'rxjs';

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';

import { BaseService } from '../base-service/base.service';
import { ApiResponseCollection } from '../api-response-interface';
import {
    BatchError,
    BatchErrorCollectionPaginationParams,
    BatchErrorCountsParams,
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
}
