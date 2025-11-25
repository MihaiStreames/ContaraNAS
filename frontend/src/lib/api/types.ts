/**
 * API Types
 * Type definitions matching backend response schemas
 */

// === Auth Types ===

export interface PairRequest {
	pairing_code: string;
}

export interface PairResponse {
	success: boolean;
	api_token: string;
	message: string;
}

export interface SuccessResponse {
	success: boolean;
	message: string;
}

// === Module Types ===

export interface ModuleInfo {
	name: string;
	display_name: string;
	enabled: boolean;
	initialized: boolean;
}

export interface ModuleListResponse {
	modules: ModuleInfo[];
}

export interface ModuleActionResponse {
	success: boolean;
	module: string;
	enabled: boolean;
}

// === Health Types ===

export interface HealthResponse {
	status: string;
	timestamp: string;
}

export interface InfoResponse {
	name: string;
	version: string;
	timestamp: string;
}

// === Error Types ===

export interface ApiError {
	detail: string;
	status: number;
}

export class ApiRequestError extends Error {
	constructor(
		message: string,
		public status: number,
		public detail?: string
	) {
		super(message);
		this.name = 'ApiRequestError';
	}
}