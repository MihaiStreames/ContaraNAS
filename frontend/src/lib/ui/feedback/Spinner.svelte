<script lang="ts">
	import type { SpinnerSchema } from '$lib/api';

	interface Props extends Omit<SpinnerSchema, 'type'> {}

	let {
		size = 'md',
		label = null
	}: Props = $props();
</script>

<div class="spinner-container" class:spinner-with-label={label}>
	<span class="spinner" class:spinner-sm={size === 'sm'} class:spinner-lg={size === 'lg'}></span>
	{#if label}
		<span class="spinner-label">{label}</span>
	{/if}
</div>

<style>
	.spinner-container {
		display: inline-flex;
		align-items: center;
		gap: var(--space-2);
	}

	.spinner-label {
		font-size: var(--text-sm);
		color: var(--text-secondary);
	}
</style>
