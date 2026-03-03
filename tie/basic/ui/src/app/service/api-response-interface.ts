/* Common base interfaces for API services */

// Purpose: Interface for API response that requires pagination
export interface ApiResponseCollection<T> {
    // count: number;
    // next: string;
    totalCount: number | null;
    data: T[];
}

// Purpose: Interface for paginated API query params
export interface ApiPaginationParams extends ApiStandardParams {
    limit?: number;
    offset?: number;
    sort?: string;
    sortOrder?: string;
}

// Purpose: Interface for standard API query params
export interface ApiStandardParams {
    byAlias?: boolean;
    exclude?: string;
    excludeDefaults?: boolean;
    excludeNone?: boolean;
    excludeUnset?: boolean;
    extra?: string;
    field?: string;
}
