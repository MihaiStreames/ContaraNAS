<script lang="ts">
	import {onMount} from 'svelte';
	import {checkHealth, disableModule, enableModule, fetchModules, type Module} from '$lib/api';

	// State using Svelte 5 runes
	let modules = $state<Module[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let backendOnline = $state(false);
	let actionLoading = $state<string | null>(null);

	onMount(async () => {
		await loadData();
	});

	async function loadData() {
		loading = true;
		error = null;

		// Check if backend is online
		backendOnline = await checkHealth();

		if (!backendOnline) {
			error = 'Backend is offline. Make sure the API server is running on port 8000.';
			loading = false;
			return;
		}

		try {
			modules = await fetchModules();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load modules';
		} finally {
			loading = false;
		}
	}

	async function toggleModule(module: Module) {
		actionLoading = module.name;
		error = null;

		try {
			if (module.enabled) {
				await disableModule(module.name);
			} else {
				await enableModule(module.name);
			}
			// Refresh the module list
			modules = await fetchModules();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to toggle module';
		} finally {
			actionLoading = null;
		}
	}
</script>

<main class="container">
    <h1>🖥️ ContaraNAS</h1>
    <p class="subtitle">System Monitoring Dashboard</p>

    <!-- Connection Status -->
    <div class="status-bar">
        <span class="status-indicator" class:online={backendOnline} class:offline={!backendOnline}></span>
        <span>{backendOnline ? 'Backend Connected' : 'Backend Offline'}</span>
        <button class="refresh-btn" onclick={loadData} disabled={loading}>
            {loading ? '⏳' : '🔄'} Refresh
        </button>
    </div>

    <!-- Error Display -->
    {#if error}
        <div class="error-box">
            ⚠️ {error}
        </div>
    {/if}

    <!-- Loading State -->
    {#if loading}
        <div class="loading">
            <p>Loading modules...</p>
        </div>
    {:else if modules.length === 0}
        <div class="empty">
            <p>No modules found. Make sure your backend is configured correctly.</p>
        </div>
    {:else}
        <!-- Module Cards -->
        <div class="modules-grid">
            {#each modules as module (module.name)}
                <div class="module-card" class:enabled={module.enabled}>
                    <div class="module-header">
                        <h2>{module.display_name}</h2>
                        <span class="module-status" class:active={module.enabled}>
                            {module.enabled ? '● Active' : '○ Inactive'}
                        </span>
                    </div>

                    <div class="module-info">
                        <p><strong>ID:</strong> {module.name}</p>
                        <p><strong>Initialized:</strong> {module.initialized ? 'Yes' : 'No'}</p>
                    </div>

                    <button
                            class="toggle-btn"
                            class:disable={module.enabled}
                            onclick={() => toggleModule(module)}
                            disabled={actionLoading === module.name}
                    >
                        {#if actionLoading === module.name}
                            ⏳ Processing...
                        {:else if module.enabled}
                            ⏹️ Disable
                        {:else}
                            ▶️ Enable
                        {/if}
                    </button>
                </div>
            {/each}
        </div>
    {/if}
</main>

<style>
    :global(body) {
        margin: 0;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        min-height: 100vh;
        color: #e4e4e4;
    }

    .container {
        max-width: 900px;
        margin: 0 auto;
        padding: 2rem;
    }

    h1 {
        text-align: center;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        color: #fff;
    }

    .subtitle {
        text-align: center;
        color: #888;
        margin-bottom: 2rem;
    }

    .status-bar {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        margin-bottom: 1.5rem;
    }

    .status-indicator {
        width: 10px;
        height: 10px;
        border-radius: 50%;
    }

    .status-indicator.online {
        background: #4ade80;
        box-shadow: 0 0 8px #4ade80;
    }

    .status-indicator.offline {
        background: #ef4444;
        box-shadow: 0 0 8px #ef4444;
    }

    .refresh-btn {
        margin-left: auto;
        padding: 0.5rem 1rem;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 6px;
        color: #fff;
        cursor: pointer;
        transition: all 0.2s;
    }

    .refresh-btn:hover:not(:disabled) {
        background: rgba(255, 255, 255, 0.2);
    }

    .refresh-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .error-box {
        padding: 1rem;
        background: rgba(239, 68, 68, 0.2);
        border: 1px solid rgba(239, 68, 68, 0.5);
        border-radius: 8px;
        margin-bottom: 1.5rem;
        color: #fca5a5;
    }

    .loading, .empty {
        text-align: center;
        padding: 3rem;
        color: #888;
    }

    .modules-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
    }

    .module-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        transition: all 0.3s;
    }

    .module-card:hover {
        border-color: rgba(255, 255, 255, 0.2);
        transform: translateY(-2px);
    }

    .module-card.enabled {
        border-color: rgba(74, 222, 128, 0.3);
        background: rgba(74, 222, 128, 0.05);
    }

    .module-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }

    .module-header h2 {
        margin: 0;
        font-size: 1.25rem;
        color: #fff;
    }

    .module-status {
        font-size: 0.85rem;
        color: #888;
    }

    .module-status.active {
        color: #4ade80;
    }

    .module-info {
        margin-bottom: 1.5rem;
    }

    .module-info p {
        margin: 0.5rem 0;
        font-size: 0.9rem;
        color: #aaa;
    }

    .toggle-btn {
        width: 100%;
        padding: 0.75rem;
        border: none;
        border-radius: 8px;
        font-size: 1rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
        background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%);
        color: #000;
    }

    .toggle-btn.disable {
        background: linear-gradient(135deg, #f87171 0%, #ef4444 100%);
        color: #fff;
    }

    .toggle-btn:hover:not(:disabled) {
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    .toggle-btn:disabled {
        opacity: 0.6;
        cursor: not-allowed;
        transform: none;
    }
</style>