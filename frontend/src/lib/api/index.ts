/**
 * API Module
 * Re-exports all API functionality
 */

// Configuration
export {API_CONFIG, STORAGE_KEYS} from './config';

// Client utilities
export {
	request,
	get,
	post,
	getStoredToken,
	setStoredToken,
	clearStoredToken,
	hasStoredToken
} from './client';

// API modules
export * as auth from './auth';
export * as modules from './modules';
export * as health from './health';

// Types
export type {
	PairRequest,
	PairResponse,
	SuccessResponse,
	ModuleInfo,
	ModuleListResponse,
	ModuleActionResponse,
	HealthResponse,
	InfoResponse,
	ApiError
} from './types';

export {ApiRequestError} from './types';