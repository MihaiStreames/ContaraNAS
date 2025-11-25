/**
 * HTTP Client
 * Base client for all API requests with automatic auth handling
 */

import {API_CONFIG, STORAGE_KEYS} from './config';
import {ApiRequestError} from './types';

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

interface RequestOptions {
	method?: HttpMethod;
	body?: unknown;
	headers?: Record<string, string>;
	requiresAuth?: boolean;
}

/**
 * Get the stored API token
 */
export function getStoredToken(): string | null {
	if (typeof window === 'undefined') return null;
	return localStorage.getItem(STORAGE_KEYS.apiToken);
}

/**
 * Store the API token
 */
export function setStoredToken(token: string): void {
	if (typeof window === 'undefined') return;
	localStorage.setItem(STORAGE_KEYS.apiToken, token);
}

/**
 * Clear the stored API token
 */
export function clearStoredToken(): void {
	if (typeof window === 'undefined') return;
	localStorage.removeItem(STORAGE_KEYS.apiToken);
}

/**
 * Check if we have a stored token
 */
export function hasStoredToken(): boolean {
	return getStoredToken() !== null;
}

/**
 * Make an HTTP request to the API
 */
export async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
	const {method = 'GET', body, headers = {}, requiresAuth = true} = options;

	const url = `${API_CONFIG.baseUrl}${endpoint}`;

	const requestHeaders: Record<string, string> = {
		'Content-Type': 'application/json',
		...headers
	};

	// Add auth header if required and token exists
	if (requiresAuth) {
		const token = getStoredToken();
		if (token) {
			requestHeaders['Authorization'] = `Bearer ${token}`;
		}
	}

	const controller = new AbortController();
	const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.timeout);

	try {
		const response = await fetch(url, {
			method,
			headers: requestHeaders,
			body: body ? JSON.stringify(body) : undefined,
			signal: controller.signal
		});

		clearTimeout(timeoutId);

		if (!response.ok) {
			let detail: string | undefined;
			try {
				const errorData = await response.json();
				detail = errorData.detail;
			} catch {
				// Response might not be JSON
			}
			throw new ApiRequestError(
				detail || `Request failed with status ${response.status}`,
				response.status,
				detail
			);
		}

		return (await response.json()) as T;
	} catch (error) {
		clearTimeout(timeoutId);

		if (error instanceof ApiRequestError) {
			throw error;
		}

		if (error instanceof Error) {
			if (error.name === 'AbortError') {
				throw new ApiRequestError('Request timeout', 408);
			}
			throw new ApiRequestError(error.message, 0);
		}

		throw new ApiRequestError('Unknown error occurred', 0);
	}
}

/**
 * GET request helper
 */
export function get<T>(endpoint: string, requiresAuth = true): Promise<T> {
	return request<T>(endpoint, {method: 'GET', requiresAuth});
}

/**
 * POST request helper
 */
export function post<T>(endpoint: string, body?: unknown, requiresAuth = true): Promise<T> {
	return request<T>(endpoint, {method: 'POST', body, requiresAuth});
}