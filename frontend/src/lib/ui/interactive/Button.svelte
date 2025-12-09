<script lang="ts">
	import type { ButtonSchema, ActionRef } from '$lib/api';
	import type { Snippet } from 'svelte';
	import Icon from '../Icon.svelte';

	interface Props extends Omit<ButtonSchema, 'type' | 'on_click'> {
		onclick?: () => void;
		children?: Snippet;
	}

	let {
		label,
		variant = 'primary',
		size = 'md',
		icon = null,
		icon_only = false,
		disabled = false,
		loading = false,
		onclick,
		children
	}: Props = $props();
</script>

<button
	class="btn btn-{variant} btn-{size}"
	class:btn-icon-only={icon_only}
	class:btn-loading={loading}
	{disabled}
	{onclick}
>
	{#if loading}
		<span class="spinner"></span>
	{/if}
	{#if icon && !loading}
		<Icon name={icon} size={size === 'sm' ? 14 : size === 'lg' ? 18 : 16} />
	{/if}
	{#if !icon_only}
		{#if children}
			{@render children()}
		{:else}
			{label}
		{/if}
	{/if}
</button>
