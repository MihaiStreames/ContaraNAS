<script lang="ts">
	import type { BadgeSchema } from '$lib/api';

	interface Props extends Omit<BadgeSchema, 'type'> {}

	let {
		text,
		variant = 'default'
	}: Props = $props();
</script>

<span class="badge" class:badge-primary={variant === 'primary'} class:badge-success={variant === 'success'} class:badge-warning={variant === 'warning'} class:badge-error={variant === 'error'} class:badge-info={variant === 'info'}>
	{text}
</span>
