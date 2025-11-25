/**
 * API Configuration
 * Centralized configuration for all API interactions
 */

export const API_CONFIG = {
	baseUrl: 'http://localhost:8000',
	wsUrl: 'ws://localhost:8000/ws',
	timeout: 10000
} as const;

// Storage keys for persistent data
export const STORAGE_KEYS = {
	apiToken: 'contaranas_api_token'
} as const;