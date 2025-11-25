/**
 * Stores Module
 * Re-exports all store functionality
 */

// Auth store
export {
	initAuth,
	pair,
	unpair,
	clearError as clearAuthError,
	getAuthState
} from './auth.svelte';

// Connection store
export {
	checkBackendHealth,
	connectWebSocket,
	disconnectWebSocket,
	clearError as clearConnectionError,
	getConnectionState
} from './connection.svelte';

// Modules store
export {
	fetchModules,
	enableModule,
	disableModule,
	toggleModule,
	setupWebSocketHandlers,
	clearError as clearModulesError,
	getModulesState
} from './modules.svelte';