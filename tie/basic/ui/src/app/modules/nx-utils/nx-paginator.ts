// Purpose: Paginated response
export interface NxPaginatorOptParams {
    pageChangeCallback?: any;
    pageIndex?: number;
    pageSize?: number;
    pageSizeFactor?: number;
    pageSizeOptions?: number[];
    pageTotal?: number;
}

export class NxPaginator {
    private _pageChangeCallback: (pageIndex: number, pageSize: number) => void;
    private _pageIndex: number;
    private _pageSize: number;
    private _pageSize_: number; // original page size, used in reset
    private _pageSizeOptions: number[];
    private _pageTotal: number;

    constructor(optParams: NxPaginatorOptParams) {
        if (optParams.pageChangeCallback) {
            this._pageChangeCallback = optParams.pageChangeCallback;
        }
        this.pageIndex = optParams.pageIndex || 0;
        this.pageSize = optParams.pageSize || this.calcPageSize(optParams.pageSizeFactor || 80);
        this.pageSizeOptions = optParams.pageSizeOptions || [5, 10, 15, 20, 25, 50, 100];
        this.pageTotal = optParams.pageTotal;
    }

    public set pageChangeCallback(value: any) {
        this._pageChangeCallback = value;
        console.log('set callback typeof', typeof value);
    }

    public set pageIndex(value: number) {
        this._pageIndex = value;
    }

    public get pageIndex(): number {
        return this._pageIndex;
    }

    public set pageSize(value: number) {
        this._pageSize_ = value;
        this._pageSize = value;
    }

    public get pageSize(): number {
        return this._pageSize;
    }

    public set pageSizeOptions(value: number[]) {
        this._pageSizeOptions = value;
    }

    public get pageSizeOptions(): number[] {
        return this._pageSizeOptions;
    }

    public set pageTotal(value: number) {
        this._pageTotal = value;
    }

    public set pageTotalReset(value: number) {
        this.reset(); // anytime a new total is provided, reset paginator
        this._pageTotal = value;
    }

    public get pageTotal(): number {
        return this._pageTotal;
    }

    public get offset(): number {
        return this._pageIndex * this._pageSize;
    }

    public get paginationParams(): any {
        return {
            limit: this._pageSize,
            offset: this.offset,
        };
    }

    public pageChanged(event: any) {
        this._pageIndex = event.pageIndex;
        this._pageSize = event.pageSize;

        // callback to reload data
        if (this._pageChangeCallback) {
            this._pageChangeCallback(this._pageIndex, this._pageSize);
        }
    }

    public pageChangedTcl(event: any) {
        this._pageIndex = event.page;
        this._pageSize = event.rows;

        // callback to reload data
        if (this._pageChangeCallback) {
            this._pageChangeCallback(this._pageIndex, this._pageSize);
        }
    }

    public reset() {
        this._pageIndex = 0;
        this._pageSize = this._pageSize_;
        this._pageTotal = 0;
    }

    private calcPageSize(factor: number): number {
        // round to closes unit of 5
        return Math.round(Math.round(window.innerHeight / factor) / 5) * 5;
    }
}
