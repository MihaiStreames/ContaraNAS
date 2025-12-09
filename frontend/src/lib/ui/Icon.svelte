<script lang="ts">
	import * as icons from 'lucide-svelte';

	interface Props {
		name: string;
		size?: number;
		strokeWidth?: number;
		class?: string;
	}

	let { name, size = 20, strokeWidth = 1.75, class: className = '' }: Props = $props();

	// Get the icon component dynamically
	const IconComponent = $derived(icons[name as keyof typeof icons] as typeof icons.Activity | undefined);
</script>

{#if IconComponent}
	<svelte:component this={IconComponent} {size} {strokeWidth} class={className} />
{:else}
	<span class="icon-placeholder" style="width: {size}px; height: {size}px;"></span>
{/if}

<style>
	.icon-placeholder {
		display: inline-block;
		background: var(--bg-surface-3);
		border-radius: var(--radius-sm);
	}
</style>
