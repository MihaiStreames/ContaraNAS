<script lang="ts">
	import type { StatCardSchema } from '$lib/api';
	import Icon from '../Icon.svelte';
	import { TrendingUp, TrendingDown } from 'lucide-svelte';

	interface Props extends Omit<StatCardSchema, 'type'> {}

	let {
		label,
		value,
		icon = null,
		color = 'default',
		trend = null
	}: Props = $props();

	const trendDirection = $derived(trend ? trend[0] : null);
	const trendValue = $derived(trend ? trend[1] : null);
</script>

<div class="stat-card" class:stat-success={color === 'success'} class:stat-warning={color === 'warning'} class:stat-error={color === 'error'}>
	{#if icon}
		<div class="stat-icon">
			<Icon name={icon} size={24} strokeWidth={1.5} />
		</div>
	{/if}
	<div class="stat-content">
		<span class="stat-value-lg">{value}</span>
		<span class="stat-label">{label}</span>
	</div>
	{#if trend}
		<div class="stat-trend" class:trend-up={trendDirection === 'up'} class:trend-down={trendDirection === 'down'}>
			{#if trendDirection === 'up'}
				<TrendingUp size={14} />
			{:else}
				<TrendingDown size={14} />
			{/if}
			{trendValue}
		</div>
	{/if}
</div>
