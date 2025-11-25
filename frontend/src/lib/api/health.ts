/**
 * Health API
 * Server health and info endpoints
 */

import {API_CONFIG} from './config';
import type {HealthResponse, InfoResponse} from './types';

/**
 * Check if the backend is reachable and healthy
 * This doesn't require authentication
 */
export async function checkHealth(): Promise<boolean> {
	try {
		const response = await fetch(`${API_CONFIG.baseUrl}/health`, {
			method: 'GET',
			signal: AbortSignal.timeout(5000)
		});
		return response.ok;
	} catch {
		return false;
	}
}

/**
 * Get detailed health response
 */
export async function getHealth(): Promise<HealthResponse | null> {
	try {
		const response = await fetch(`${API_CONFIG.baseUrl}/health`);
		if (!response.ok) return null;
		return (await response.json()) as HealthResponse;
	} catch {
		return null;
	}
}

/**
 * Get server info
 */
export async function getServerInfo(): Promise<InfoResponse | null> {
	try {
		const response = await fetch(`${API_CONFIG.baseUrl}/info`);
		if (!response.ok) return null;
		return (await response.json()) as InfoResponse;
	} catch {
		return null;
	}
}