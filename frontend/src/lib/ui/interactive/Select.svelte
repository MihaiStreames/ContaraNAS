<script lang="ts">
	import type { SelectSchema, SelectOptionSchema } from '$lib/api';

	interface Props extends Omit<SelectSchema, 'type'> {
		onchange?: (value: string) => void;
	}

	let {
		name,
		label = null,
		options,
		value = $bindable(null),
		disabled = false,
		onchange
	}: Props = $props();

	function handleChange(e: Event) {
		const target = e.target as HTMLSelectElement;
		value = target.value;
		onchange?.(value);
	}
</script>

<div class="form-group">
	{#if label}
		<label class="form-label" for={name}>{label}</label>
	{/if}
	<select
		id={name}
		{name}
		class="form-select"
		{disabled}
		onchange={handleChange}
	>
		{#each options as option}
			<option value={option.value} selected={option.value === value}>
				{option.label}
			</option>
		{/each}
	</select>
</div>
