import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, ReplaySubject } from 'rxjs';
import { map, tap } from 'rxjs/operators';

export interface Validator {
  name: string;
  config?: any;
}
export interface Form {
  fields: {
    choices?: string[];
    default?: string | string[];
    info?: string;
    label: string;
    minWidth?: number;
    name: string;
    required: boolean;
    type?: string;
    validators: Validator[];
  }[];
}

export interface FieldDisplay {
  field: string;
  label: string;
  type?: string;
}

export interface AppConfig {
  schema: string;
  ui: {
    global: {
      sideNav: { label: string; path: string }[];
      featureFlags?: {
        enableAddJob?: boolean;
      };
    };
    adhocRequest?: {
      form: Form;
    };
    downloadTI?: {
      form: Form;
    };
    jobTable: {
      columns: FieldDisplay[];
      details: FieldDisplay[];
      filters: Form;
    };
    notifications?: {
      columns: FieldDisplay[];
      details: FieldDisplay[];
      filters: Form;
    };
    configure?: {
      columns: FieldDisplay[];
      formFields: any[];
      infoTooltip?: string;
    };
    egressErrors?: {
      columns: FieldDisplay[];
      details: FieldDisplay[];
    };
    brand?: string;
    owner: string;
    title: string;
    version: string;
  };
}

@Injectable({
  providedIn: 'root',
})
export class AppService {
  apiUrl: string = 'api/tc';

  private appConfigSubject = new ReplaySubject<AppConfig>(1);

  constructor(private http: HttpClient) {
    this.loadUIConfig().subscribe();
  }

  public getConfig(): Observable<AppConfig> {
    return this.appConfigSubject.asObservable();
  }

  /** Fetch fresh TC owner names. Call each time the owner dropdown is opened. */
  public getOwners(): Observable<string[]> {
    return this.http
      .get<{ owners: string[] }>('api/tc-info')
      .pipe(map((d) => (Array.isArray(d?.owners) ? d.owners : [])));
  }

  private loadUIConfig(): Observable<AppConfig> {
    return this.http.get<AppConfig>(`${this.apiUrl}/app-config`).pipe(
      tap((config) => {
        this.appConfigSubject.next(config);
      }),
    );
  }
}
