import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
    name: 'jsonFormat',
})
export class JsonFormatPipe implements PipeTransform {
    transform(value: any): string {
        if (value) {
            return JSON.stringify(JSON.parse(value), null, 2); // Format with 2 spaces of indentation
        }
        return '';
    }
}
