/**
 * Auth API
 * Authentication-related API calls
 */

import {clearStoredToken, post, setStoredToken} from './client';
import type {PairResponse, SuccessResponse} from './types';

/**
 * Pair with the NAS using a pairing code
 * Returns the API token on success
 */
export async function pair(pairingCode: string): Promise<PairResponse> {
	const response = await post<PairResponse>(
		'/api/auth/pair',
		{pairing_code: pairingCode},
		false // No auth required for pairing
	);

	// Store the token on successful pairing
	if (response.success && response.api_token) {
		setStoredToken(response.api_token);
	}

	return response;
}

/**
 * Unpair from the NAS
 * Clears the stored token
 */
export async function unpair(): Promise<SuccessResponse> {
	const response = await post<SuccessResponse>('/api/auth/unpair');

	// Clear the stored token regardless of response
	clearStoredToken();

	return response;
}