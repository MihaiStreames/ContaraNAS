<script lang="ts">
	import type { ToggleSchema } from '$lib/api';

	interface Props extends Omit<ToggleSchema, 'type'> {
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
	<label class="toggle">
		<input
			type="checkbox"
			id={name}
			{name}
			{checked}
			{disabled}
			onchange={handleChange}
		/>
		<span class="toggle-slider"></span>
	</label>
	{#if label}
		<label class="form-label" for={name}>{label}</label>
	{/if}
</div>
