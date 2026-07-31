import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { BatchErrorsComponent } from './pages/batch-errors/batch-errors.component';
import { ConfigureComponent } from './pages/configure/configure.component';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { DownloadComponent } from './pages/download/download.component';
import { EgressErrorsComponent } from './pages/egress-errors/egress-errors.component';
import { JobsComponent } from './pages/jobs/jobs.component';
import { NotificationsComponent } from './pages/notifications/notifications.component';
import { ReportPdfTrackerComponent } from './pages/report-pdf-tracker/report-pdf-tracker.component';
import { TasksComponent } from './pages/tasks/tasks.component';

const routes: Routes = [
    // Ingress routes
    { path: 'dashboard', component: DashboardComponent },
    { path: 'download', component: DownloadComponent },
    { path: 'batchErrors', component: BatchErrorsComponent },
    { path: 'reportPdfTrackers', component: ReportPdfTrackerComponent },

    // Egress routes
    { path: 'configure', component: ConfigureComponent },
    { path: 'errors', component: EgressErrorsComponent },

    // Shared routes
    { path: 'jobs', component: JobsComponent },
    { path: 'tasks', component: TasksComponent },
    { path: 'notifications', component: NotificationsComponent },

    // Default — side nav config drives which page is the landing page
    { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
];

@NgModule({
    imports: [RouterModule.forRoot(routes, { onSameUrlNavigation: 'reload' })],
    exports: [RouterModule],
})
export class AppRoutingModule {}
