<script lang="ts">
	import type { TileSchema, BadgeSchema, StatSchema } from '$lib/api';
	import type { Snippet } from 'svelte';
	import Icon from '../Icon.svelte';
	import Badge from '../display/Badge.svelte';

	interface Props extends Omit<TileSchema, 'type' | 'badge' | 'stats' | 'content' | 'actions'> {
		badge?: BadgeSchema | null;
		stats?: StatSchema[];
		content?: Snippet;
		actions?: Snippet;
	}

	let {
		icon,
		title,
		badge = null,
		stats = [],
		content,
		actions
	}: Props = $props();
</script>

<div class="module-tile">
	<div class="tile-header">
		<div class="tile-icon">
			<Icon name={icon} size={22} />
		</div>
		<div class="tile-title-group">
			<h3 class="tile-title">{title}</h3>
			{#if badge}
				<Badge text={badge.text} variant={badge.variant} />
			{/if}
		</div>
	</div>

	{#if stats.length > 0}
		<div class="tile-stats">
			{#each stats as stat}
				<div class="tile-stat">
					<span class="tile-stat-value">{stat.value}</span>
					<span class="tile-stat-label">{stat.label}</span>
				</div>
			{/each}
		</div>
	{/if}

	{#if content}
		<div class="tile-content">
			{@render content()}
		</div>
	{/if}

	{#if actions}
		<div class="tile-actions">
			{@render actions()}
		</div>
	{/if}
</div>
