import { ApiPaginationParams } from '../api-response-interface';

export interface ReportPdfTracker {
    id: string;
    groupId: string;
    attemptCount: number;
    attemptResult: string;
    dateLastAttempt: string;
}

export interface ReportPdfTrackerPaginationParams extends ApiPaginationParams {
    group_id?: string;
    attempt_result?: string;
}
