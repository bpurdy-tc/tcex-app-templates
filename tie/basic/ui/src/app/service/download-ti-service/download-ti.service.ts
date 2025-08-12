import { Observable } from 'rxjs';

import { Injectable } from '@angular/core';

import { BaseService } from '../base-service/base.service';
import { ApiResponseCollection } from '../api-response-interface';

@Injectable({
    providedIn: 'root',
})
export class DownloadTIService extends BaseService {
    apiUrl: string = '/api/download/ti';

    get(params: { [key: string]: string }): Observable<any> {
        return this.http.get<{ original: any; transformed: any; csrf_token: string }>(this.apiUrl, {
            params,
        });
    }

    upload(data: any, csrf_token: string) {
        return this.http.post(this.apiUrl, { data, csrf_token });
    }
}
