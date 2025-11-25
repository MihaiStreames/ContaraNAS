<script lang="ts">
	interface Props {
		message: string;
		onDismiss?: () => void;
	}

	let {message, onDismiss}: Props = $props();
</script>

<div class="error-alert" role="alert">
    <span class="icon">⚠️</span>
    <span class="message">{message}</span>
    {#if onDismiss}
        <button class="dismiss" onclick={onDismiss} aria-label="Dismiss error">×</button>
    {/if}
</div>

<style>
    .error-alert {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.875rem 1rem;
        background: rgba(239, 68, 68, 0.15);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 8px;
        color: #fca5a5;
    }

    .icon {
        flex-shrink: 0;
    }

    .message {
        flex: 1;
        font-size: 0.9rem;
    }

    .dismiss {
        flex-shrink: 0;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0;
        background: transparent;
        border: none;
        border-radius: 4px;
        color: #fca5a5;
        font-size: 1.25rem;
        cursor: pointer;
        transition: background-color 0.2s;
    }

    .dismiss:hover {
        background: rgba(255, 255, 255, 0.1);
    }
</style>