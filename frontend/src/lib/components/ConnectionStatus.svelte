<script lang="ts">
	import {checkBackendHealth, getConnectionState} from '$lib/stores';

	const connection = getConnectionState();

	interface Props {
		showRefresh?: boolean;
	}

	let {showRefresh = true}: Props = $props();

	let isRefreshing = $state(false);

	async function handleRefresh() {
		isRefreshing = true;
		await checkBackendHealth();
		isRefreshing = false;
	}

	const statusText = $derived.by(() => {
		if (!connection.backendOnline) return 'Backend Offline';
		switch (connection.wsConnectionState) {
			case 'connected':
				return 'Connected';
			case 'connecting':
				return 'Connecting...';
			case 'error':
				return 'Connection Error';
			default:
				return 'Disconnected';
		}
	});

	const statusClass = $derived.by(() => {
		if (!connection.backendOnline) return 'offline';
		switch (connection.wsConnectionState) {
			case 'connected':
				return 'online';
			case 'connecting':
				return 'connecting';
			default:
				return 'offline';
		}
	});
</script>

<div class="connection-status">
    <span class="indicator {statusClass}"></span>
    <span class="text">{statusText}</span>

    {#if showRefresh}
        <button
                class="refresh-btn"
                onclick={handleRefresh}
                disabled={isRefreshing || connection.isChecking}
                aria-label="Refresh connection"
        >
            {#if isRefreshing || connection.isChecking}
                ⏳
            {:else}
                🔄
            {/if}
        </button>
    {/if}
</div>

<style>
    .connection-status {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 0.75rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 6px;
        font-size: 0.875rem;
    }

    .indicator {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        flex-shrink: 0;
    }

    .indicator.online {
        background: #4ade80;
        box-shadow: 0 0 6px #4ade80;
    }

    .indicator.connecting {
        background: #fbbf24;
        box-shadow: 0 0 6px #fbbf24;
        animation: pulse 1.5s infinite;
    }

    .indicator.offline {
        background: #ef4444;
        box-shadow: 0 0 6px #ef4444;
    }

    .text {
        color: #e4e4e4;
    }

    .refresh-btn {
        margin-left: auto;
        padding: 0.25rem 0.5rem;
        background: transparent;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 4px;
        color: #e4e4e4;
        cursor: pointer;
        font-size: 0.875rem;
        transition: all 0.2s;
    }

    .refresh-btn:hover:not(:disabled) {
        background: rgba(255, 255, 255, 0.1);
    }

    .refresh-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    @keyframes pulse {
        0%,
        100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }
</style>