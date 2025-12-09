<script lang="ts">
	import type { CardSchema } from '$lib/api';
	import type { Snippet } from 'svelte';
	import Icon from '../Icon.svelte';

	interface Props extends Omit<CardSchema, 'type' | 'children' | 'footer'> {
		children?: Snippet;
		footer?: Snippet;
	}

	let {
		icon = null,
		title = null,
		children,
		footer
	}: Props = $props();
</script>

<div class="card">
	{#if icon || title}
		<div class="card-header">
			{#if icon}
				<span class="card-icon">
					<Icon name={icon} size={20} />
				</span>
			{/if}
			{#if title}
				<h3 class="card-title">{title}</h3>
			{/if}
		</div>
	{/if}
	{#if children}
		<div class="card-content">
			{@render children()}
		</div>
	{/if}
	{#if footer}
		<div class="card-footer">
			{@render footer()}
		</div>
	{/if}
</div>
