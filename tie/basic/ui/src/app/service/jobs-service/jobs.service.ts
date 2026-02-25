import { Observable } from 'rxjs';

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';

import { BaseService } from '../base-service/base.service';
import { ApiResponseCollection } from '../api-response-interface';
import { Job, JobCollectionPaginationParams } from './jobs-interface';

@Injectable({
    providedIn: 'root',
})
export class JobsService extends BaseService {
    apiUrl: string = '/api/job';

    createJob(job): Observable<any> {
        return this.http.post(`${this.apiUrl}/adhoc`, job);
    }

    getCollection(params: JobCollectionPaginationParams): Observable<any> {
        return this.http.get<ApiResponseCollection<Job>>(`${this.apiUrl}/request`, {
            params: this.convertToHttpParams(params),
        });
    }

    getJobFiles(jobId: string): Observable<string[]> {
        return this.http.get<string[]>(`${this.apiUrl}/${jobId}/files`);
    }
}
