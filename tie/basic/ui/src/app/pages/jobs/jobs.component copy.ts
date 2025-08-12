import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { CheckboxState, MenuItemEvent, MenuItemType, Table } from '@tc-eng/component-library';
import { FeatureVersion } from '@tc-eng/component-library/utils/featureFlags';
import { BehaviorSubject, catchError, finalize, interval, map, mergeMap, tap } from 'rxjs';
import { NxPaginator } from 'src/app/modules/nx-utils/nx-paginator';
import { NxTable } from 'src/app/modules/nx-utils/nx-table';
import { AlertMessageService } from 'src/app/service/alert-message-service/alert-message.service';
import { AppService } from 'src/app/service/app-service/app.service';
import { BaseHttpErrorResponse } from 'src/app/service/base-service/base-http-error-response';
import { Job } from 'src/app/service/jobs-service/jobs-interface';
import { JobsService } from 'src/app/service/jobs-service/jobs.service';
import { TaskService } from 'src/app/service/tasks-service/taks.service';

export enum SideDrawerContent {
  DETAILS,
  DOWNLOAD,
  ADD_JOB,
}

@Component({
  selector: 'jobs',
  templateUrl: './jobs.component.html',
  styleUrl: './jobs.component.scss',
})
export class JobsComponent implements OnDestroy, OnInit {
  // ui framework settings
  protected readonly featureVersion: FeatureVersion = 'new-design';

  // search
  jobId?: string;
  jobTypes: string[] = [];
  jobStatus?: string[] = [];
  table?: NxTable;
  detailsData?: any;

  multiSelectAdvancedSettings = {
    headerSelectAll: true,
    filter: true,
    filterPlaceholder: 'Search...',
    filterNoResults: 'No results found',
  };
  jobTypeMenuItems: any[] = [
    {
      text: 'Scheduled',
      value: 'scheduled',
      type: MenuItemType.MultiSelect,
      checked: CheckboxState.Checked,
    },
    {
      text: 'Ad-Hoc',
      value: 'ad-hoc',
      type: MenuItemType.MultiSelect,
      checked: CheckboxState.Checked,
    },
  ];

  jobStatusesLoaded = false;
  jobStatusMenuItems: any[] = [];

  // table
  @ViewChild('dataTable') tableComponent: Table;

  paginator = new NxPaginator({ pageChangeCallback: this.getJobData.bind(this) });

  menuItemsWithDownload = [
    { label: 'Details', value: 'details', disabled: false },
    {
      label: 'Download Files',
      value: 'download',
      title: 'Only available for finished jobs.',
    },
    {
      label: 'Batch Errors',
      value: 'batchErrors',
    },
  ];

  // private refreshTimer$ = interval(1000 * 60 * 5);
  private refreshTimer$ = interval(1000 * 20);

  private refreshTimerSubscription: any;

  // download sidebar
  private downloadFilesSubject: BehaviorSubject<any> = new BehaviorSubject<any[]>([]);
  downloadFiles$ = this.downloadFilesSubject.asObservable();

  // add job form state
  startTime?: number = null;
  endTime?: number = null;

  adhocFormValidSubject = new BehaviorSubject<boolean>(false);
  adhocFormValid$ = this.adhocFormValidSubject.asObservable();

  // side nav settings
  protected readonly SideDrawerContent = SideDrawerContent;

  showSideDrawer: boolean = false;
  showSideDrawerTitle: string = 'Job Details';
  sideDrawerContent: SideDrawerContent;
  selectedJob: Job;
  adhocFormConfig: any;
  adhocForm: any;

  constructor(
    private alertMessageService: AlertMessageService,
    private jobsService: JobsService,
    private router: Router,
    private taskServie: TaskService,
    private appService: AppService
  ) {}

  ngOnDestroy(): void {
    this.refreshTimerSubscription.unsubscribe();
  }

  ngOnInit() {
    this.getJobData$().subscribe();
    this.getTaskStatuses();

    this.refreshTimerSubscription = this.refreshTimer$.pipe(mergeMap(() => this.getJobData$())).subscribe();

    const uiConfig = this.appService.getUIConfig();
    this.table = this.buildTable(uiConfig?.ui?.job_table?.columns);
    this.detailsData = this.buildDetailsData(uiConfig?.ui?.job_table?.details);
    this.adhocFormConfig = this.buildAdhocFormConfig(uiConfig?.ui?.ad_hoc_request?.form);
    console.log(this.adhocFormConfig);
    // build this.table data based on ui config
  }

  splitAndClean(input: string | undefined | null): string[] {
    if (!input) {
      return [];
    }
    return input.split('|').filter((value) => value.trim() !== '');
  }

  buildAdhocFormConfig(form: any) {
    if (!form) {
      console.error('Ad-hoc request form configuration is missing in app-config.json');
      return [];
    }

    const mapChoices = (choices: string[] | undefined, defaultAsList: string[]) => {
      return (
        choices?.map((choice: string) => ({
          text: choice,
          value: choice,
          type: MenuItemType.MultiSelect,
          checked: defaultAsList.includes(choice) ? CheckboxState.Checked : CheckboxState.UnChecked,
        })) || []
      );
    };

    const adhocFormConfig = form.fields.map((field) => {
      const defaultAsList = this.splitAndClean(field.default);

      return {
        name: field.name,
        label: field.name,
        type: field.type,
        choices: mapChoices(field.choices, defaultAsList),
        required: field.required,
        default: field.default,
        default_as_list: defaultAsList,
      };
    });

    // Populate `adhocForm` based on `default` or `default_as_list` values
    this.adhocForm = adhocFormConfig.map((config) => {
      if (config.type === 'multi-select') {
        return { [config.name]: config.default_as_list };
      } else {
        return { [config.name]: config.default };
      }
    });

    return adhocFormConfig;
  }

  buildDetailsData(details: any): any {
    let detailsData: any;
    if (!details) {
      console.error('Job details columns configuration is missing in app-config.json');
      return;
    }
    detailsData = details.map((data) => ({
      name: data.field,
      header: data.header,
      formatType: data.type,
    }));

    return detailsData;
  }

  buildTable(columns: any): NxTable {
    let table: NxTable | undefined;
    if (!columns) {
      console.error('Job table columns configuration is missing in app-config.json');
      return;
    }

    table = new NxTable({
      dataColumns: columns.map((column) => ({
        field: column.field,
        header: column.header,
        ...(column.type === 'date' && { formatType: 'date' }), // Add formatType if type is 'date'
      })),
    });
    return table;
  }

  getJobData() {
    // set dataLoaded to false to show loading spinner on pagination
    this.table.dataLoaded = false;
    this.getJobData$()
      .pipe(
        catchError((error: BaseHttpErrorResponse) => {
          return [];
        })
      )
      .subscribe({});
  }

  getMenuItemsFor(job: Job) {
    if (job.status === 'Failed' || (job.status.startsWith('Upload') && job.status.endsWith('Complete'))) {
      return;
    } else {
      return [
        { label: 'Details', value: 'details', disabled: false },
        {
          disabled: true,
          label: 'Download Files',
          value: 'download',
          title: 'Only available for finished jobs.',
        },
      ];
    }
  }

  handleAddJobClick() {
    this.showSideDrawerTitle = 'Add Job';

    this.sideDrawerContent = SideDrawerContent.ADD_JOB;
    this.showSideDrawer = true;
  }

  handleJobStatusSelectionChanged(event: MenuItemEvent) {
    this.jobStatus = event.selected?.map((i) => i.value) || [];
  }

  handleJobTypeSelectionChanged(event: MenuItemEvent) {
    this.jobTypes = event.selected?.map((i) => i.value) || [];
  }

  handleNestedMenuSelection(event_, job: Job) {
    switch (event_) {
      case 'batchErrors':
        this.router.navigate(['/batchErrors'], {
          queryParams: {
            jobId: job.requestId,
          },
        });
        break;
      case 'details':
        this.showSideDrawerTitle = 'Job Details';

        this.sideDrawerContent = SideDrawerContent.DETAILS;
        this.selectedJob = job;
        this.showSideDrawer = true;
        break;
      case 'download':
        this.showSideDrawerTitle = 'Download Job Files';
        this.sideDrawerContent = SideDrawerContent.DOWNLOAD;
        this.selectedJob = job;
        this.showSideDrawer = true;
        this.getJobFiles();
    }
  }

  handleSearchClick() {
    this.table.dataLoaded = false;
    this.tableComponent.first = 0;
    this.paginator.reset();
    this.getJobData();
  }

  handleSidenavChange(newValue) {
    if (newValue !== this.showSideDrawer) {
      this.showSideDrawer = newValue;
    }
  }

  handleStartTimeSelect(event) {
    this.startTime = event.getTime();
    this.checkAdhocFormValid();
  }

  handleInputChange(event, field) {
    if (field.type === 'date') {
      // Update the value to a timestamp if the field type is date
      this.adhocForm[field.name] = event.getTime();
    } else if (field.type === 'multi-select') {
      // Update the value to an array of selected values if the field type is multi-select
      this.adhocForm[field.name] = event.selected?.map((i: any) => i.value) || [];
    } else {
      // Update the value as a string for other field types
      this.adhocForm[field.name] = event.target ? event.target.value : event;
    }

    // Revalidate the form
    this.checkAdhocFormValid();
  }

  private getTaskStatuses() {
    this.taskServie
      .getTaskStatuses()
      .pipe(
        tap((resp) => {
          const menuItems = resp.data.map((status) => {
            return {
              checked: CheckboxState.Checked,
              text: status,
              value: status,
              type: MenuItemType.MultiSelect,
            };
          });
          this.jobStatusMenuItems = menuItems;
          this.jobStatusesLoaded = true;
        })
      )
      .subscribe();
  }

  private getJobData$() {
    return this.jobsService
      .getCollection({
        ...this.paginator.paginationParams,
        job_type:
          this.jobTypes.length !== 0 && this.jobTypes.length !== this.jobTypeMenuItems.length
            ? this.jobTypes.join(',')
            : undefined,
        request_id: this.jobId,
        sort: 'created',
        sort_order: 'desc',
        status:
          this.jobStatus.length !== 0 && this.jobStatus.length != this.jobStatusMenuItems.length
            ? this.jobStatus.join(',')
            : undefined,
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

  private getJobFiles() {
    this.jobsService
      .getJobFiles(this.selectedJob.requestId)
      .pipe(
        map((files) => {
          let groupedFiles = files.reduce((acc, file) => {
            let group = file.split('/')[0];
            if (group === file) {
              group = 'Metadata';
            } else {
              group = group.split('_')[0];
              group = group.charAt(0).toUpperCase() + group.slice(1);
            }
            const groupFiles = acc[group] || [];
            groupFiles.push(file);
            acc[group] = groupFiles;
            return acc;
          }, {});

          Object.keys(groupedFiles).forEach((group) => {
            const groups = groupedFiles[group].sort().map((file) => {
              return {
                name: file,
                group: group,
                href: `api/job/${this.selectedJob.requestId}/download?file_name=${encodeURIComponent(file)}`,
              };
            });

            groupedFiles[group] = groups;
          });

          groupedFiles = Object.keys(groupedFiles).map((group) => {
            return {
              group: group,
              files: groupedFiles[group],
            };
          });

          console.log(groupedFiles);
          return groupedFiles;
        }),
        tap((files) => {
          this.downloadFilesSubject.next(files);
        })
      )
      .subscribe();
  }

  private checkAdhocFormValid() {
    // Check if all required fields in adhocFormConfig are populated
    const isValid = this.adhocFormConfig.every((field) => {
      if (!field.required) {
        return true; // Skip non-required fields
      }

      const value = this.adhocForm[field.name];

      if (field.type === 'multi-select') {
        // For multi-select, ensure it's an array with at least one value
        return Array.isArray(value) && value.length > 0;
      } else if (field.type === 'date') {
        // For date, ensure it's a valid timestamp
        return typeof value === 'number' && !isNaN(value);
      } else {
        // For string or other types, ensure it's not empty
        return value !== null && value !== undefined && value.toString().trim() !== '';
      }
    });

    this.adhocFormValidSubject.next(isValid);
  }

  addJob() {
    this.adhocFormValidSubject.next(false);
    this.jobsService
      .createJob(this.adhocForm)
      .pipe(
        tap(() => {
          this.alertMessageService.add({
            summary: 'Created Ad-Hoc Job',
            severity: 'success',
          });
        }),
        mergeMap(() => this.getJobData$()),
        finalize(() => {
          this.showSideDrawer = false;
        })
      )
      .subscribe();
  }
}
