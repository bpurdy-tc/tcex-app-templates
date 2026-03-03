import { HttpErrorResponse } from '@angular/common/http';
import { ErrorHandler, Injectable } from '@angular/core';

import { AlertToastMessage } from '@tc-eng/component-library';

import { AlertMessageService } from '../service/alert-message-service/alert-message.service';

@Injectable()
export class GlobalErrorHandler implements ErrorHandler {
    constructor(private alertMessageService: AlertMessageService) {}

    handleError(error) {
        /**
         * Benign error ignore.
         */
        if (error.message === 'elementStates is undefined') {
            return;
        }
        if (error instanceof HttpErrorResponse) {
            if (!navigator.onLine) {
                const atm = {
                    closable: false,
                    detail: 'No Internet Connection.',
                    pauseable: true,
                    severity: 'error',
                    summary: 'Connection Error',
                } as AlertToastMessage;

                this.alertMessageService.add(atm);
            } else {
                let errorMessage: string;
                if (error.error) {
                    if (error.error.errorMsg) {
                        errorMessage = error.error.errorMsg;
                    } else if (error.error.message) {
                        errorMessage = error.error.message;
                    } else if (error.status !== undefined) {
                        errorMessage = getUserFriendlyErrorForStatus(error.status);
                    } else {
                        errorMessage =
                            'There was an error on the server. If the problem persists, contact technical support.';
                    }
                }

                this.alertMessageService.add({
                    closable: true,
                    detail: errorMessage,
                    life: 5000,
                    pauseable: true,
                    severity: 'error',
                    summary: 'HTTP Error',
                });
            }
        } else if (error.message !== undefined && error.summary !== undefined) {
            this.alertMessageService.add({
                detail: error.message,
                summary: error.summary,
                closable: error.closable !== undefined ? error.closable : true,
                life: error.life !== undefined ? error.life : 5000,
                pauseable: error.pauseable !== undefined ? error.pauseable : true,
                severity: error.severity !== undefined ? error.severity : 'error',
            });
        } else {
            let errorMessage: string;
            if (error.message) {
                errorMessage = error.message;
            } else if (error instanceof Event) {
                if (error.currentTarget) {
                    errorMessage = error.currentTarget.toString();
                } else if (error.target) {
                    errorMessage = error.target.toString();
                }
            }
            const atm = {
                closable: true,
                detail:
                    errorMessage ||
                    'An unknown error has occurred.  Please make sure logged into main application',
                life: 5000,
                pauseable: true,
                severity: 'error',
                summary: 'Unexpected Error',
            } as AlertToastMessage;
            this.alertMessageService.add(atm);
        }

        console.error('Global Error Handler Handled', error);
    }
}

const getUserFriendlyErrorForStatus = (statusCode: number): string => {
    // These HTTP Status Error Messages could probably be improved.
    switch (statusCode) {
        case 0:
            return `Communication with the server was cancelled. Please try again. If the problem persists, contact technical support.`;
        case 400:
            return `There was an error communicating with the server. Please try again. If the problem persists, contact technical support.`;
        case 401:
            return `You can't take that action without being logged in.`;
        case 403:
            return `You don't have the right permissions to take that action.`;
        case 404:
            return `That action was not able to be found. Please try again. If the problem persists, contact technical support.`;
        case 405:
            return `The application tried to send an unsupported action to the server. If the problem persists, contact technical support.`;
        case 408:
            return `It took too long to communicate with the server. Please try again. If the problem persists, contact technical support.`;
        case 409:
            return `Could not process action. There was a conflict between the local data and the data on the server. If the problem persists, contact technical support.`;
        case 410:
            return `The requested resource is no longer available. If the problem persists, contact technical support.`;
        case 413:
            return `There is not enough space configured in your organization to upload this file. Contact technical support.`;
        case 414:
            return `The URL used is too long to work, please report this error to your server admin. If the problem persists, contact technical support.`;
        case 415:
            return `The file type uploaded is not supported. Please upload a supported file type. If the problem persists, contact technical support.`;
        case 429:
            return `There are too many connections between the application and the server. Please try again later. If the problem persists, contact technical support.`;
        case 500:
            return `There was an error on the server. If the problem persists, contact technical support.`;
        default:
            return 'There was an error on the server. If the problem persists, contact technical support.';
    }
};
