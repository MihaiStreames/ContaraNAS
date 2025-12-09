<script lang="ts">
	import type { InputSchema } from '$lib/api';

	interface Props extends Omit<InputSchema, 'type' | 'input_type'> {
		type?: 'text' | 'password' | 'email' | 'number';
		onchange?: (value: string) => void;
	}

	let {
		name,
		label = null,
		value = $bindable(''),
		type = 'text',
		placeholder = null,
		disabled = false,
		onchange
	}: Props = $props();

	function handleInput(e: Event) {
		const target = e.target as HTMLInputElement;
		value = target.value;
		onchange?.(value);
	}
</script>

<div class="form-group">
	{#if label}
		<label class="form-label" for={name}>{label}</label>
	{/if}
	<input
		{type}
		id={name}
		{name}
		class="form-input"
		{value}
		placeholder={placeholder ?? undefined}
		{disabled}
		oninput={handleInput}
	/>
</div>
