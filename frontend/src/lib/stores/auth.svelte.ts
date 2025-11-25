/**
 * Auth Store
 * Manages authentication state using Svelte 5 runes
 */

import {clearStoredToken, hasStoredToken} from '../api/client';
import {auth} from '../api';
import {resetWebSocketClient} from '../websocket';

// === State ===

let isPaired = $state(false);
let isLoading = $state(false);
let error = $state<string | null>(null);

// === Initialization ===

/**
 * Initialize auth state from stored token
 */
export function initAuth(): void {
	isPaired = hasStoredToken();
}

// === Actions ===

/**
 * Pair with the NAS using a pairing code
 */
export async function pair(pairingCode: string): Promise<boolean> {
	isLoading = true;
	error = null;

	try {
		const response = await auth.pair(pairingCode);
		if (response.success) {
			isPaired = true;
			return true;
		}
		error = response.message || 'Pairing failed';
		return false;
	} catch (e) {
		error = e instanceof Error ? e.message : 'Pairing failed';
		return false;
	} finally {
		isLoading = false;
	}
}

/**
 * Unpair from the NAS
 */
export async function unpair(): Promise<boolean> {
	isLoading = true;
	error = null;

	try {
		// Disconnect WebSocket first
		resetWebSocketClient();

		await auth.unpair();
		isPaired = false;
		return true;
	} catch (e) {
		// Even if the API call fails, clear local state
		clearStoredToken();
		isPaired = false;
		error = e instanceof Error ? e.message : 'Unpair failed';
		return false;
	} finally {
		isLoading = false;
	}
}

/**
 * Clear any auth errors
 */
export function clearError(): void {
	error = null;
}

// === Exported State (reactive getters) ===

export function getAuthState() {
	return {
		get isPaired() {
			return isPaired;
		},
		get isLoading() {
			return isLoading;
		},
		get error() {
			return error;
		}
	};
}