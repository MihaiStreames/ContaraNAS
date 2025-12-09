<script lang="ts">
	import type { CheckboxSchema } from '$lib/api';

	interface Props extends Omit<CheckboxSchema, 'type'> {
		onchange?: (checked: boolean) => void;
	}

	let {
		name,
		label = null,
		checked = $bindable(false),
		disabled = false,
		onchange
	}: Props = $props();

	function handleChange(e: Event) {
		const target = e.target as HTMLInputElement;
		checked = target.checked;
		onchange?.(checked);
	}
</script>

<div class="form-group form-group-inline">
	<input
		type="checkbox"
		class="checkbox"
		id={name}
		{name}
		{checked}
		{disabled}
		onchange={handleChange}
	/>
	{#if label}
		<label for={name}>{label}</label>
	{/if}
</div>
