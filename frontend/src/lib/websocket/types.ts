/**
 * WebSocket Types
 * Type definitions for WebSocket messages
 */

// === Outgoing Messages (Client -> Server) ===

export interface PingMessage {
	type: 'ping';
}

export type OutgoingMessage = PingMessage;

// === Incoming Messages (Server -> Client) ===

export interface PongMessage {
	type: 'pong';
	timestamp: string;
}

export interface ModuleStateInfo {
	name: string;
	display_name: string;
	enabled: boolean;
	initialized: boolean;
	source?: 'builtin' | 'community';
	removable?: boolean;
	version?: string;
	system_deps?: string[];
}

export interface InitialStateMessage {
	type: 'initial_state';
	timestamp: string;
	modules: ModuleStateInfo[];
	system: SystemStats | null;
	steam: SteamData | null;
}

export interface ModuleStateMessage {
	type: 'module_state';
	timestamp: string;
	module: string;
	enabled: boolean;
	initialized: boolean;
	change_type: string;
}

export interface SystemStatsMessage {
	type: 'system_stats';
	timestamp: string;
	cpu: CpuInfo | null;
	memory: MemoryInfo | null;
	disks: DiskInfo[];
}

export interface SteamLibraryMessage {
	type: 'steam_library';
	timestamp: string;
	libraries: SteamLibrary[];
	games: SteamGame[];
	total_games: number;
	total_libraries: number;
}

export type IncomingMessage =
	| PongMessage
	| InitialStateMessage
	| ModuleStateMessage
	| SystemStatsMessage
	| SteamLibraryMessage;

// === Data Types ===

export interface SystemStats {
	cpu: CpuInfo | null;
	memory: MemoryInfo | null;
	disks: DiskInfo[];
}

export interface CpuInfo {
	name: string;
	physical_cores: number;
	logical_cores: number;
	usage_per_core: number[];
	total_usage: number;
	current_speed_ghz: number;
	max_speed_ghz: number;
	min_speed_ghz: number;
	processes: number;
	threads: number;
	file_descriptors: number;
	uptime: number;
}

export interface MemoryInfo {
	total: number;
	available: number;
	free: number;
	used: number;
	usage: number;
	buffers: number;
	cached: number;
	shared: number;
	swap_total: number;
	swap_used: number;
	swap_free: number;
	swap_usage: number;
	ram_sticks: RamInfo[];
}

export interface RamInfo {
	locator: string;
	bank_locator: string;
	size: number;
	type: string;
	speed: number;
	manufacturer: string;
	part_number: string;
}

export interface DiskInfo {
	device: string;
	mountpoint: string;
	filesystem: string;
	total_gb: number;
	used_gb: number;
	free_gb: number;
	usage_percent: number;
	read_bytes: number;
	write_bytes: number;
	read_speed: number;
	write_speed: number;
	read_time: number;
	write_time: number;
	io_time: number;
	busy_time: number;
	model: string;
	type: string;
}

export interface SteamData {
	libraries: SteamLibrary[];
	games: SteamGame[];
	total_games: number;
	total_libraries: number;
}

export interface SteamLibrary {
	path: string;
	game_count: number;
	total_games_size: number;
	total_shader_size: number;
	total_workshop_size: number;
	total_size: number;
	drive_total: number;
	drive_free: number;
	drive_used: number;
}

export interface SteamGame {
	app_id: number;
	name: string;
	install_dir: string;
	library_path: string;
	size_on_disk: number;
	shader_cache_size: number;
	workshop_content_size: number;
	total_size: number;
	update_size: number;
	install_state: 'installed' | 'updating' | 'downloading' | 'paused' | 'uninstalled';
	last_updated: number;
	last_played: number;
	build_id: string;
	store_url: string;
	installed_depots: Record<string, Record<string, string>>;
}

// === Connection State ===

export type ConnectionState = 'disconnected' | 'connecting' | 'connected' | 'error';

export interface WebSocketState {
	connectionState: ConnectionState;
	lastError: string | null;
	lastMessageAt: Date | null;
}