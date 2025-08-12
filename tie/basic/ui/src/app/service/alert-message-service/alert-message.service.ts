import { Injectable } from '@angular/core';

import { AlertToastMessageService } from '@tc-eng/component-library';

import { AlertMessage } from './alert-message-interface';

@Injectable({
    providedIn: 'root',
})
export class AlertMessageService {
    currentMessageIds: string[] = [];

    constructor(private alertToastMessageService: AlertToastMessageService) {}

    add(message: AlertMessage) {
        console.log('Alert Service Message', message);
        if (!this.currentMessageIds.includes(message.id)) {
            this.alertToastMessageService.add(message);
            if (message.id) {
                this.addMessageId(message.id);
            }
        }
    }

    private addMessageId(messageId: string) {
        this.currentMessageIds.push(messageId);
        if (this.currentMessageIds.length > 10) {
            this.currentMessageIds.shift();
        }
    }
}
