import { HttpErrorResponse } from '@angular/common/http';

import { v5 as uuidv5 } from 'uuid';

export class BaseHttpErrorResponse extends HttpErrorResponse {
    errorId: string;

    constructor(errorResponse: HttpErrorResponse) {
        super({
            error: errorResponse.error,
            headers: errorResponse.headers,
            status: errorResponse.status,
            statusText: errorResponse.statusText,
            url: errorResponse.url,
        });
        this.errorId = this.generateUuidFromUrl(errorResponse);
    }

    private generateUuidFromUrl(errorResponse: HttpErrorResponse): string {
        const namespace = '1b671a64-40d5-491e-99b0-da01ff1f3341';
        const uuid = uuidv5(errorResponse.url + errorResponse.message, namespace);
        return uuid;
    }
}
