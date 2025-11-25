<script lang="ts">
	import type {ModuleInfo} from '$lib/api';
	import {getModulesState, toggleModule} from '$lib/stores';

	interface Props {
		module: ModuleInfo;
	}

	let {module}: Props = $props();

	const modulesState = getModulesState();

	const isActionInProgress = $derived(modulesState.actionInProgress === module.name);

	async function handleToggle() {
		await toggleModule(module);
	}

	// Module icons based on name (can be extended)
	const moduleIcon = $derived.by(() => {
		switch (module.name) {
			case 'steam':
				return '🎮';
			case 'sys_monitor':
				return '💻';
			default:
				return '📦';
		}
	});
</script>

<div class="module-card" class:enabled={module.enabled}>
    <div class="card-header">
        <span class="icon">{moduleIcon}</span>
        <div class="title-section">
            <h3>{module.display_name}</h3>
            <span class="status" class:active={module.enabled}>
				{module.enabled ? '● Active' : '○ Inactive'}
			</span>
        </div>
    </div>

    <div class="card-body">
        <div class="info-row">
            <span class="label">ID</span>
            <code class="value">{module.name}</code>
        </div>
        <div class="info-row">
            <span class="label">Initialized</span>
            <span class="value">{module.initialized ? '✓ Yes' : '✗ No'}</span>
        </div>
    </div>

    <button
            class="toggle-btn"
            class:disable={module.enabled}
            onclick={handleToggle}
            disabled={isActionInProgress}
    >
        {#if isActionInProgress}
            <span class="spinner"></span>
            Processing...
        {:else if module.enabled}
            ⏹️ Disable
        {:else}
            ▶️ Enable
        {/if}
    </button>
</div>

<style>
    .module-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.25rem;
        transition: all 0.25s ease;
    }

    .module-card:hover {
        border-color: rgba(255, 255, 255, 0.15);
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    }

    .module-card.enabled {
        border-color: rgba(74, 222, 128, 0.25);
        background: rgba(74, 222, 128, 0.03);
    }

    .card-header {
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        margin-bottom: 1rem;
    }

    .icon {
        font-size: 1.5rem;
        line-height: 1;
    }

    .title-section {
        flex: 1;
    }

    .title-section h3 {
        margin: 0 0 0.25rem 0;
        font-size: 1.1rem;
        font-weight: 600;
        color: #fff;
    }

    .status {
        font-size: 0.8rem;
        color: #888;
    }

    .status.active {
        color: #4ade80;
    }

    .card-body {
        margin-bottom: 1rem;
    }

    .info-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.4rem 0;
        font-size: 0.85rem;
    }

    .info-row:not(:last-child) {
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }

    .label {
        color: #888;
    }

    .value {
        color: #ccc;
    }

    code.value {
        font-family: 'SF Mono', Monaco, monospace;
        font-size: 0.8rem;
        padding: 0.15rem 0.4rem;
        background: rgba(0, 0, 0, 0.3);
        border-radius: 4px;
    }

    .toggle-btn {
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        padding: 0.7rem;
        border: none;
        border-radius: 8px;
        font-size: 0.9rem;
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
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }

    .toggle-btn:disabled {
        opacity: 0.6;
        cursor: not-allowed;
        transform: none;
    }

    .spinner {
        width: 14px;
        height: 14px;
        border: 2px solid transparent;
        border-top-color: currentColor;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }
</style>