/**
 * Modules Store
 * Manages module state with WebSocket integration
 */

import {type ModuleInfo, modules as modulesApi} from '../api';
import {getWebSocketClient, type ModuleStateInfo} from '../websocket';

// === State ===

let modulesList = $state<ModuleInfo[]>([]);
let isLoading = $state(false);
let error = $state<string | null>(null);
let actionInProgress = $state<string | null>(null);

// === API Actions ===

/**
 * Fetch all modules from the API
 */
export async function fetchModules(): Promise<void> {
	isLoading = true;
	error = null;

	try {
		modulesList = await modulesApi.fetchModules();
	} catch (e) {
		error = e instanceof Error ? e.message : 'Failed to fetch modules';
		modulesList = [];
	} finally {
		isLoading = false;
	}
}

/**
 * Enable a module
 */
export async function enableModule(name: string): Promise<boolean> {
	actionInProgress = name;
	error = null;

	try {
		const response = await modulesApi.enableModule(name);
		if (response.success) {
			updateModuleState(name, {enabled: true, initialized: true});
			return true;
		}
		return false;
	} catch (e) {
		error = e instanceof Error ? e.message : `Failed to enable ${name}`;
		return false;
	} finally {
		actionInProgress = null;
	}
}

/**
 * Disable a module
 */
export async function disableModule(name: string): Promise<boolean> {
	actionInProgress = name;
	error = null;

	try {
		const response = await modulesApi.disableModule(name);
		if (response.success) {
			updateModuleState(name, {enabled: false});
			return true;
		}
		return false;
	} catch (e) {
		error = e instanceof Error ? e.message : `Failed to disable ${name}`;
		return false;
	} finally {
		actionInProgress = null;
	}
}

/**
 * Toggle a module's enabled state
 */
export async function toggleModule(module: ModuleInfo): Promise<boolean> {
	if (module.enabled) {
		return disableModule(module.name);
	}
	return enableModule(module.name);
}

// === WebSocket Integration ===

/**
 * Set up WebSocket handlers for module updates
 */
export function setupWebSocketHandlers(): void {
	const client = getWebSocketClient();

	// Handle initial state with modules list
	client.setOnInitialState((message) => {
		modulesList = message.modules.map(toModuleInfo);
	});

	// Handle individual module state changes
	client.setOnModuleState((message) => {
		updateModuleState(message.module, {
			enabled: message.enabled,
			initialized: message.initialized
		});
	});
}

// === Helper Functions ===

/**
 * Update a specific module's state
 */
function updateModuleState(
	name: string,
	updates: Partial<Pick<ModuleInfo, 'enabled' | 'initialized'>>
): void {
	modulesList = modulesList.map((m) => (m.name === name ? {...m, ...updates} : m));
}

/**
 * Convert WebSocket module info to API module info
 */
function toModuleInfo(wsModule: ModuleStateInfo): ModuleInfo {
	return {
		name: wsModule.name,
		display_name: wsModule.display_name,
		enabled: wsModule.enabled,
		initialized: wsModule.initialized
	};
}

/**
 * Clear module errors
 */
export function clearError(): void {
	error = null;
}

// === Exported State ===

export function getModulesState() {
	return {
		get modules() {
			return modulesList;
		},
		get isLoading() {
			return isLoading;
		},
		get error() {
			return error;
		},
		get actionInProgress() {
			return actionInProgress;
		},
		get enabledModules() {
			return modulesList.filter((m) => m.enabled);
		},
		get disabledModules() {
			return modulesList.filter((m) => !m.enabled);
		}
	};
}