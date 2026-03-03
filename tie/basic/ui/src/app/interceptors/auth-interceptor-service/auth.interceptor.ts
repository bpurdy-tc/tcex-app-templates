import { Observable, throwError } from 'rxjs';

import { HttpErrorResponse, HttpEvent, HttpHandler, HttpInterceptor, HttpRequest } from '@angular/common/http';
import { Injectable } from '@angular/core';

import { AlertToastMessage } from '@tc-eng/component-library';
import { catchError } from 'rxjs/operators';
import { AlertMessageService } from 'src/app/service/alert-message-service/alert-message.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
    constructor(protected alertMessageService: AlertMessageService) {}

    intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
        return next.handle(request).pipe(
            catchError((error: HttpErrorResponse) => {
                if (error.status === 401) {
                    const atm = {
                        closable: false,
                        detail: 'You have been logged out. To continue log back in.',
                        pauseable: true,
                        severity: 'error',
                        summary: 'Logged Out',
                    } as AlertToastMessage;
                    this.alertMessageService.add(atm);
                }

                return throwError(() => error);
            }),
        );
    }
}
