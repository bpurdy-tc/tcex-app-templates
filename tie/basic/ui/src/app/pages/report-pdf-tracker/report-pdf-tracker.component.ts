import { Component, ViewChild } from '@angular/core';
import { Table } from '@tc-eng/component-library';
import { FeatureVersion } from '@tc-eng/component-library/utils/featureFlags';
import { catchError, tap } from 'rxjs';
import { NxPaginator } from 'src/app/modules/nx-utils/nx-paginator';
import { NxTable } from 'src/app/modules/nx-utils/nx-table';
import { BaseHttpErrorResponse } from 'src/app/service/base-service/base-http-error-response';
import { ReportPdfTrackerService } from 'src/app/service/report-pdf-tracker-service/report-pdf-tracker.service';

@Component({
  selector: 'report-pdf-tracker',
  templateUrl: './report-pdf-tracker.component.html',
  styleUrl: './report-pdf-tracker.component.scss',
})
export class ReportPdfTrackerComponent {
  // ui framework settings
  protected readonly featureVersion: FeatureVersion = 'new-design';

  // search
  groupId?: string;
  attemptResult?: string;

  // table
  @ViewChild('dataTable') tableComponent: Table;

  paginator = new NxPaginator({ pageChangeCallback: this.getReportPDFTrackerData.bind(this) });
  table = new NxTable({
    dataColumns: [
      { field: 'groupId', header: 'Group ID' },
      { field: 'dateLastAttempt', header: 'Last Attempt' },
      { field: 'attemptCount', header: 'Attempts' },
      { field: 'attemptResult', header: 'Status' },
    ],
  });

  constructor(private reportPdfTrackerService: ReportPdfTrackerService) {}

  ngOnInit(): void {
    this.getReportPDFTrackerData();
  }

  getReportPDFTrackerData() {
    // set dataLoaded to false to show loading spinner on pagination
    this.table.dataLoaded = false;
    this.getReportPDFTrackerData$()
      .pipe(
        catchError((error: BaseHttpErrorResponse) => {
          return [];
        })
      )
      .subscribe({});
  }

  handleSearchClick() {
    this.table.dataLoaded = false;
    this.tableComponent.first = 0;
    this.paginator.reset();
    this.getReportPDFTrackerData();
  }

  private getReportPDFTrackerData$() {
    return this.reportPdfTrackerService
      .getCollection({
        ...this.paginator.paginationParams,
        group_id: this.groupId,
        attempt_result: this.attemptResult,
        sort: 'created',
      })
      .pipe(
        tap((resp) => {
          this.table.data = resp.data;
          this.table.dataLoaded = true;
          if (resp.totalCount) {
            this.paginator.pageTotal = resp.totalCount;
          }
        })
      );
  }
}
