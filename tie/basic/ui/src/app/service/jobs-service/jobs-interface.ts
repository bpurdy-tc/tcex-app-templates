import { ApiPaginationParams } from '../api-response-interface';

export interface Job {
    dateCompleted: string;
    dateQueued: string;
    dateStarted: string;
    jobType: string;
    requestId: string;
    status: string;
    statusIcon: string;
    countBatchError: number;
    countBatchGroupSuccess: number;
    countBatchIndicatorSuccess: number;
    countDownloadGroup: number;
    countDownloadIndicator: number;
    dateConvertStart: string;
    dateConvertComplete: string;
    dateDownloadStart: string;
    dateDownloadComplete: string;
    dateUploadStart: string;
    dateUploadComplete: string;
    updatedSince: string;
    updatedTill: string;
    groupTypes: string[];
    indicatorTypes: string[];
    filterIncludeTags: string[];
    filterExcludeTags: string[];
}

export interface JobCollectionPaginationParams extends ApiPaginationParams {
    request_id?: string;
    status?: string[];
    job_types?: string[];
}
