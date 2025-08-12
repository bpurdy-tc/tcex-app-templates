import { tap } from 'rxjs';

import { Component, Input, OnInit } from '@angular/core';

import { FieldDisplay } from 'src/app/service/app-service/app.service';
import { TaskService } from 'src/app/service/tasks-service/taks.service';

@Component({
    selector: 'app-formatted-field',
    templateUrl: './formatted-field.component.html',
    styleUrl: './formatted-field.component.scss',
})
export class FormattedFieldComponent implements OnInit {
    @Input() field: FieldDisplay;
    @Input() value: any;

    finalStatuses = null;

    constructor(private taskService: TaskService) {}

    ngOnInit(): void {
        this.taskService
            .getCollection()
            .pipe(
                tap((res) => {
                    const finalStatuses = [];
                    for (const task of res.data) {
                        if (task.lastTask) {
                            finalStatuses.push(task.statusComplete.toLocaleLowerCase());
                        }
                    }

                    this.finalStatuses = finalStatuses;
                }),
            )
            .subscribe();
    }
}
