import { Component, EventEmitter, Input, Output } from '@angular/core';

import {
    MonitorRulesItem,
    RuleInputItem,
} from 'src/app/service/monitor-rules-service/monitor-rules-interface';

interface EditRuleInputItem extends RuleInputItem {
    value: any;
    valid: boolean;
    error?: string;
}

export interface EditRuleItem extends MonitorRulesItem {
    inputs: EditRuleInputItem[];
}

@Component({
    selector: 'rule-card',
    templateUrl: './rule-card.component.html',
    styleUrl: './rule-card.component.scss',
})
export class RuleCardComponent {
    @Input() opened = true;
    @Input() rule: EditRuleItem;
    @Output() delete: EventEmitter<MonitorRulesItem> = new EventEmitter();
    @Output() save: EventEmitter<MonitorRulesItem> = new EventEmitter();
    @Output() validChanged: EventEmitter<boolean> = new EventEmitter();

    protected editing = false;
    valid: boolean = true;

    private _originalRule: EditRuleItem;

    onCancelClick() {
        this.editing = false;
        this.rule = this._originalRule;
    }

    onEditClicked() {
        this._originalRule = structuredClone(this.rule);
        this.editing = true;
    }

    onRuleInputValid(ruleInput: EditRuleInputItem, $event) {
        ruleInput.valid = $event;
        this._validateRule();
    }

    onRuleInputValueChanged(ruleInput: EditRuleInputItem, value: any) {
        ruleInput.value = value;
        this._validateRule();
    }

    onSaveClick() {
        this.editing = false;
        this._validateRule();
        if (this.valid) {
            this.save.emit(this.rule);
        }
    }

    private _validateRule() {
        let valid = true;
        for (const input of this.rule.inputs) {
            valid = valid && this._validateRuleInput(input);
        }
        if (this.valid !== valid) {
            this.valid = valid;
            this.validChanged.emit(this.valid);
        }
    }

    private _validateRuleInput(ruleInput: EditRuleInputItem) {
        if (ruleInput.optional) {
            ruleInput.error = null;
            return true;
        }

        if (ruleInput.type === 'number') {
            try {
                const value = parseFloat(ruleInput.value);
                if (isNaN(value)) {
                    throw new Error('Invalid number');
                }
                if (value < ruleInput.minValue || value > ruleInput.maxValue) {
                    ruleInput.error = `Must be between ${ruleInput.minValue} and ${ruleInput.maxValue}`;
                    return false;
                }
            } catch (e) {
                ruleInput.error = 'Invalid Number';
                return false;
            }
        }

        ruleInput.error = null;
        return true;
    }
}
