import { Observable } from 'rxjs';

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';

import { BaseService } from '../base-service/base.service';
import { ApiResponseCollection } from '../api-response-interface';
import { ReportPdfTracker, ReportPdfTrackerPaginationParams } from './report-pdf-tracker-interface';

@Injectable({
    providedIn: 'root',
})
export class ReportPdfTrackerService extends BaseService {
    apiUrl: string = '/api/report/pdf-tracker';

    getCollection(params: ReportPdfTrackerPaginationParams): Observable<any> {
        return this.http.get<ApiResponseCollection<ReportPdfTracker>>(`${this.apiUrl}`, {
            params: this.convertToHttpParams(params),
        });
    }
}
