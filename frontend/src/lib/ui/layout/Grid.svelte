<script lang="ts">
	import type { GridSchema, ComponentSchema } from '$lib/api';
	import type { Snippet } from 'svelte';

	interface Props extends Omit<GridSchema, 'type' | 'children'> {
		children?: Snippet;
	}

	let {
		columns = 2,
		gap = '4',
		children
	}: Props = $props();

	// Handle columns - can be number or string like "repeat(auto-fill, minmax(300px, 1fr))"
	const gridColumns = $derived(
		typeof columns === 'number'
			? `repeat(${columns}, 1fr)`
			: columns
	);
</script>

<div
	class="grid gap-{gap}"
	style="grid-template-columns: {gridColumns}"
>
	{#if children}
		{@render children()}
	{/if}
</div>
