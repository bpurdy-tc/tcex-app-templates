import { catchError, mergeMap, tap } from 'rxjs';

import { Component, Input, OnChanges, OnInit, SimpleChanges, ViewChild } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { Table } from '@tc-eng/component-library';
import { FeatureVersion } from '@tc-eng/component-library/utils/featureFlags';
import { NxPaginator } from 'src/app/modules/nx-utils/nx-paginator';
import { NxTable } from 'src/app/modules/nx-utils/nx-table';
import { BaseHttpErrorResponse } from 'src/app/service/base-service/base-http-error-response';
import { BatchErrorService } from 'src/app/service/batch-errors-service/batch-error.service';

@Component({
    selector: 'batch-errors-table',
    templateUrl: './batch-errors-table.component.html',
    styleUrl: './batch-errors-table.component.scss',
})
export class BatchErrorsTableComponent implements OnChanges, OnInit {
    // ui framework settings
    protected readonly featureVersion: FeatureVersion = 'new-design';

    @Input() errorCode: string;
    @Input() jobId: string;

    // search
    reason?: string;

    // table
    @ViewChild('dataTable') tableComponent: Table;

    paginator = new NxPaginator({ pageChangeCallback: this.getBatchErrorData.bind(this) });
    table = new NxTable({
        dataColumns: [
            { field: 'requestId', header: 'Job ID' },
            { field: 'dateAdded', header: 'Date Added' },
            { field: 'reason', header: 'Reason' },
        ],
    });

    dataSubscription = null;

    private initialized = false;

    constructor(
        private batchErrorService: BatchErrorService,
        private activeRoute: ActivatedRoute,
    ) {}
    ngOnInit(): void {
        this.dataSubscription = this.activeRoute.queryParams
            .pipe(
                tap((params) => {
                    this.jobId = params['jobId'];
                    this.initialized = true;
                }),
                mergeMap(() => {
                    return this.getBatchErrorData$().pipe(
                        catchError((error: BaseHttpErrorResponse) => {
                            return [];
                        }),
                    );
                }),
            )
            .subscribe();
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (this.initialized) {
            this.reason = null;
            this.paginator.reset();
            this.table.data = [];
            this.table.dataLoaded = false;
            this.getBatchErrorData();
        }
    }

    getBatchErrorData() {
        // set dataLoaded to false to show loading spinner on pagination
        // this.table.dataLoaded = false;
        if (this.dataSubscription) {
            this.dataSubscription.unsubscribe();
        }

        this.dataSubscription = this.getBatchErrorData$()
            .pipe(
                catchError((error: BaseHttpErrorResponse) => {
                    return [];
                }),
            )
            .subscribe();
    }

    handleSearchClick() {
        this.table.dataLoaded = false;
        this.tableComponent.first = 0;
        this.paginator.pageIndex = 0;
        this.getBatchErrorData();
    }

    handleReasonInput($event) {
        this.reason = $event;
    }

    private getBatchErrorData$() {
        return this.batchErrorService
            .getCollection({
                ...this.paginator.paginationParams,
                errorCode: this.errorCode !== 'All' ? this.errorCode : undefined,
                reason: this.reason,
                request_id: this.jobId,
                sort: 'created',
                sortOrder: 'desc',
            })
            .pipe(
                tap((resp) => {
                    this.table.data = resp.data;
                    this.table.dataLoaded = true;
                    if (resp.totalCount) {
                        this.paginator.pageTotal = resp.totalCount;
                    }
                }),
            );
    }
}
