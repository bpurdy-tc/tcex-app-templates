import { AlertToastAction, Message } from '@tc-eng/component-library';

export interface AlertMessage extends Message {
    alertId?: string;
    pauseable?: boolean;
    action?: AlertToastAction;
}
