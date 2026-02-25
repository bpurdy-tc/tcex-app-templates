export interface NxTableOptParams {
    dataColumns: any[];
    dataLoaded?: boolean;
}

export class NxTable {
    private _data: any[] = [];
    private _dataColumns: string[];
    private _dataLoaded: boolean = false;
    private _dataPaginated: any[] = [];

    constructor(optParams: NxTableOptParams) {
        this.dataColumns = optParams.dataColumns || [];
        this._dataLoaded = optParams.dataLoaded || false;
    }

    public set data(value: any[]) {
        this._data = value;
        this._dataLoaded = true;
    }

    public get data(): any[] {
        return this._data;
    }

    public set dataColumns(value: string[]) {
        this._dataColumns = value;
    }

    public get dataColumns(): string[] {
        return this._dataColumns;
    }

    public set dataLoaded(value: boolean) {
        this._dataLoaded = value;
    }

    public get dataLoaded(): boolean {
        return this._dataLoaded;
    }

    public get dataPaginated(): any[] {
        return this._dataPaginated;
    }

    public get hasData(): boolean {
        return this._data.length > 0;
    }

    public paginateData(pageIndex: number, pageSize: number) {
        const pageStart = pageIndex * pageSize;
        const pageEnd = pageStart + pageSize;
        this._dataPaginated = this._data.slice(pageStart, pageEnd);
    }
}
