/**
 * Modules API
 * Module management API calls
 */

import {get, post} from './client';
import type {ModuleActionResponse, ModuleInfo, ModuleListResponse} from './types';

/**
 * Fetch all modules with their current state
 */
export async function fetchModules(): Promise<ModuleInfo[]> {
	const response = await get<ModuleListResponse>('/api/modules');
	return response.modules;
}

/**
 * Enable a module by name
 */
export async function enableModule(name: string): Promise<ModuleActionResponse> {
	return post<ModuleActionResponse>(`/api/modules/${name}/enable`);
}

/**
 * Disable a module by name
 */
export async function disableModule(name: string): Promise<ModuleActionResponse> {
	return post<ModuleActionResponse>(`/api/modules/${name}/disable`);
}

/**
 * Toggle a module's enabled state
 */
export async function toggleModule(module: ModuleInfo): Promise<ModuleActionResponse> {
	if (module.enabled) {
		return disableModule(module.name);
	}
	return enableModule(module.name);
}