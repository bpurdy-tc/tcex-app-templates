import { Component, Input } from '@angular/core';
import { alertCircle, IconRegistry } from '@tc-eng/component-library';

@Component({
    selector: 'app-error-message',
    templateUrl: './error-message.component.html',
    styleUrls: ['./error-message.component.scss'],
})
export class ErrorMessageComponent {
    @Input() message: string;

    constructor(private iconRegistry: IconRegistry) {
        this.iconRegistry.registerIcons([alertCircle]);
    }
}
