<script lang="ts">
	import {onMount} from 'svelte';
	import {ConnectionStatus, ErrorAlert, ModuleCard, PairingForm} from '$lib/components';
	import {
		checkBackendHealth,
		clearModulesError,
		connectWebSocket,
		disconnectWebSocket,
		fetchModules,
		getAuthState,
		getConnectionState,
		getModulesState,
		initAuth,
		setupWebSocketHandlers,
		unpair
	} from '$lib/stores';

	// Get reactive state
	const auth = getAuthState();
	const connection = getConnectionState();
	const modules = getModulesState();

	// Local state
	let isInitializing = $state(true);
	let showUnpairConfirm = $state(false);

	onMount(async () => {
		// Initialize auth state from storage
		initAuth();

		// Check backend health
		await checkBackendHealth();

		if (auth.isPaired && connection.backendOnline) {
			// Set up WebSocket handlers before connecting
			setupWebSocketHandlers();

			// Connect WebSocket
			connectWebSocket();

			// Fetch modules as backup (WebSocket will also provide them)
			await fetchModules();
		}

		isInitializing = false;
	});

	// React to auth changes
	$effect(() => {
		if (auth.isPaired && connection.backendOnline && !connection.isConnected) {
			setupWebSocketHandlers();
			connectWebSocket();
			fetchModules();
		}
	});

	async function handleUnpair() {
		disconnectWebSocket();
		await unpair();
		showUnpairConfirm = false;
	}

	async function handleRefresh() {
		await checkBackendHealth();
		if (auth.isPaired && connection.backendOnline) {
			await fetchModules();
		}
	}
</script>

<svelte:head>
    <title>ContaraNAS</title>
</svelte:head>

<main class="app">
    <!-- Header -->
    <header class="header">
        <div class="header-content">
            <h1 class="logo">🖥️ ContaraNAS</h1>
            <p class="tagline">System Monitoring Dashboard</p>
        </div>
    </header>

    <!-- Connection Status Bar -->
    <div class="status-bar">
        <ConnectionStatus/>

        {#if auth.isPaired}
            <button class="btn-text" onclick={() => (showUnpairConfirm = true)}> Unpair</button>
        {/if}
    </div>

    <!-- Main Content -->
    <div class="content">
        {#if isInitializing}
            <!-- Loading State -->
            <div class="loading-state">
                <div class="spinner"></div>
                <p>Initializing...</p>
            </div>
        {:else if !connection.backendOnline}
            <!-- Backend Offline -->
            <div class="offline-state">
                <div class="icon">📡</div>
                <h2>Backend Offline</h2>
                <p>Cannot connect to the ContaraNAS server.</p>
                <p class="hint">Make sure the API server is running on port 8000.</p>
                <button class="btn-primary" onclick={handleRefresh}> 🔄 Retry Connection</button>
            </div>
        {:else if !auth.isPaired}
            <!-- Pairing Required -->
            <PairingForm/>
        {:else}
            <!-- Dashboard -->
            <div class="dashboard">
                <!-- Error Display -->
                {#if modules.error}
                    <ErrorAlert message={modules.error} onDismiss={clearModulesError}/>
                {/if}

                <!-- Module Grid -->
                {#if modules.isLoading && modules.modules.length === 0}
                    <div class="loading-state">
                        <div class="spinner"></div>
                        <p>Loading modules...</p>
                    </div>
                {:else if modules.modules.length === 0}
                    <div class="empty-state">
                        <div class="icon">📦</div>
                        <h2>No Modules Found</h2>
                        <p>No modules are registered with the backend.</p>
                    </div>
                {:else}
                    <section class="modules-section">
                        <div class="section-header">
                            <h2>Modules</h2>
                            <span class="module-count">
								{modules.enabledModules.length} / {modules.modules.length} active
							</span>
                        </div>

                        <div class="modules-grid">
                            {#each modules.modules as module (module.name)}
                                <ModuleCard {module}/>
                            {/each}
                        </div>
                    </section>
                {/if}
            </div>
        {/if}
    </div>

    <!-- Unpair Confirmation Modal -->
    {#if showUnpairConfirm}
        <div class="modal-overlay" onclick={() => (showUnpairConfirm = false)} role="presentation">
            <div class="modal" onclick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
                <h3>Unpair from NAS?</h3>
                <p>You'll need to enter a new pairing code to reconnect.</p>
                <div class="modal-actions">
                    <button class="btn-secondary" onclick={() => (showUnpairConfirm = false)}>
                        Cancel
                    </button>
                    <button class="btn-danger" onclick={handleUnpair}> Unpair</button>
                </div>
            </div>
        </div>
    {/if}
</main>

<style>
    :global(body) {
        margin: 0;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
        min-height: 100vh;
        color: #e4e4e4;
    }

    .app {
        min-height: 100vh;
        display: flex;
        flex-direction: column;
    }

    /* Header */
    .header {
        padding: 1.5rem 2rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }

    .header-content {
        max-width: 1200px;
        margin: 0 auto;
    }

    .logo {
        margin: 0;
        font-size: 1.75rem;
        font-weight: 700;
        color: #fff;
    }

    .tagline {
        margin: 0.25rem 0 0 0;
        color: #666;
        font-size: 0.9rem;
    }

    /* Status Bar */
    .status-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        max-width: 1200px;
        margin: 0 auto;
        padding: 1rem 2rem;
        width: 100%;
        box-sizing: border-box;
    }

    .btn-text {
        padding: 0.5rem 1rem;
        background: transparent;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 6px;
        color: #888;
        font-size: 0.85rem;
        cursor: pointer;
        transition: all 0.2s;
    }

    .btn-text:hover {
        color: #e4e4e4;
        border-color: rgba(255, 255, 255, 0.4);
    }

    /* Content */
    .content {
        flex: 1;
        max-width: 1200px;
        margin: 0 auto;
        padding: 1rem 2rem 2rem;
        width: 100%;
        box-sizing: border-box;
    }

    /* Loading State */
    .loading-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 4rem;
        color: #888;
    }

    .spinner {
        width: 32px;
        height: 32px;
        border: 3px solid rgba(255, 255, 255, 0.1);
        border-top-color: #4ade80;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
        margin-bottom: 1rem;
    }

    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }

    /* Offline State */
    .offline-state {
        text-align: center;
        padding: 4rem 2rem;
    }

    .offline-state .icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }

    .offline-state h2 {
        margin: 0 0 0.5rem 0;
        color: #fff;
    }

    .offline-state p {
        margin: 0.25rem 0;
        color: #888;
    }

    .offline-state .hint {
        font-size: 0.85rem;
        color: #666;
        margin-bottom: 1.5rem;
    }

    .btn-primary {
        padding: 0.75rem 1.5rem;
        background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%);
        border: none;
        border-radius: 8px;
        color: #000;
        font-size: 1rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
    }

    .btn-primary:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(74, 222, 128, 0.3);
    }

    /* Empty State */
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
    }

    .empty-state .icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }

    .empty-state h2 {
        margin: 0 0 0.5rem 0;
        color: #fff;
    }

    .empty-state p {
        color: #888;
    }

    /* Dashboard */
    .dashboard {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }

    /* Modules Section */
    .modules-section {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .section-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .section-header h2 {
        margin: 0;
        font-size: 1.25rem;
        color: #fff;
    }

    .module-count {
        font-size: 0.85rem;
        color: #666;
    }

    .modules-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 1rem;
    }

    /* Modal */
    .modal-overlay {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.7);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 100;
    }

    .modal {
        background: #1a1a2e;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        max-width: 360px;
        width: 90%;
    }

    .modal h3 {
        margin: 0 0 0.5rem 0;
        color: #fff;
    }

    .modal p {
        margin: 0 0 1.5rem 0;
        color: #888;
        font-size: 0.9rem;
    }

    .modal-actions {
        display: flex;
        gap: 0.75rem;
    }

    .btn-secondary {
        flex: 1;
        padding: 0.75rem;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        color: #e4e4e4;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.2s;
    }

    .btn-secondary:hover {
        background: rgba(255, 255, 255, 0.15);
    }

    .btn-danger {
        flex: 1;
        padding: 0.75rem;
        background: linear-gradient(135deg, #f87171 0%, #ef4444 100%);
        border: none;
        border-radius: 8px;
        color: #fff;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.2s;
    }

    .btn-danger:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
    }
</style>