import { Component, Input } from '@angular/core';

@Component({
    selector: 'monitor-status-badge',
    templateUrl: './monitor-status-badge.component.html',
    styleUrl: './monitor-status-badge.component.scss',
})
export class MonitorStatusBadgeComponent {
    @Input() status: string;
    @Input() tooltip?: string;
}
