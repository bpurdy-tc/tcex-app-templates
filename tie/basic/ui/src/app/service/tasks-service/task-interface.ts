export interface Task {
    maxExecutionMinutes: number;
    description: string;
    name: string;
    paused: boolean;
    process?: any;
    pipeline?: string;
    schedulePeriod: number;
    scheduleUnit: string;
    slug: string;
    type: string;
    index: number;
    lastTask: boolean;
    statusComplete?: string;
}
