<script lang="ts">
	import {clearAuthError, getAuthState, pair} from '$lib/stores';

	const auth = getAuthState();

	// Pairing code segments (XXXX-XXXX-XXXX format)
	let segments = $state(['', '', '']);
	let inputRefs: HTMLInputElement[] = [];

	// Computed full code
	const fullCode = $derived(segments.join('-'));
	const isValid = $derived(segments.every((s) => s.length === 4));

	function handleInput(index: number, event: Event) {
		const input = event.target as HTMLInputElement;
		let value = input.value.toUpperCase().replace(/[^A-Z0-9]/g, '');

		// Limit to 4 characters
		if (value.length > 4) {
			value = value.slice(0, 4);
		}

		segments[index] = value;

		// Auto-advance to next segment
		if (value.length === 4 && index < 2) {
			inputRefs[index + 1]?.focus();
		}
	}

	function handleKeyDown(index: number, event: KeyboardEvent) {
		// Handle backspace to go to previous segment
		if (event.key === 'Backspace' && segments[index] === '' && index > 0) {
			inputRefs[index - 1]?.focus();
		}
	}

	function handlePaste(event: ClipboardEvent) {
		event.preventDefault();
		const pasted = event.clipboardData?.getData('text') || '';

		// Clean and parse pasted code
		const cleaned = pasted.toUpperCase().replace(/[^A-Z0-9]/g, '');

		if (cleaned.length >= 12) {
			// Full code pasted
			segments[0] = cleaned.slice(0, 4);
			segments[1] = cleaned.slice(4, 8);
			segments[2] = cleaned.slice(8, 12);
			inputRefs[2]?.focus();
		}
	}

	async function handleSubmit() {
		if (!isValid) return;
		clearAuthError();
		await pair(fullCode);
	}

	function handleClear() {
		segments = ['', '', ''];
		clearAuthError();
		inputRefs[0]?.focus();
	}
</script>

<div class="pairing-form">
    <div class="header">
        <h2>🔐 Pair with NAS</h2>
        <p>Enter the pairing code displayed on your NAS</p>
    </div>

    <div class="code-input">
        {#each segments as segment, i}
            <input
                    bind:this={inputRefs[i]}
                    type="text"
                    maxlength="4"
                    placeholder="XXXX"
                    value={segment}
                    oninput={(e) => handleInput(i, e)}
                    onkeydown={(e) => handleKeyDown(i, e)}
                    onpaste={handlePaste}
                    disabled={auth.isLoading}
                    autocomplete="off"
                    autocapitalize="characters"
                    spellcheck="false"
            />
            {#if i < 2}
                <span class="separator">-</span>
            {/if}
        {/each}
    </div>

    {#if auth.error}
        <div class="error">
            ⚠️ {auth.error}
        </div>
    {/if}

    <div class="actions">
        <button class="btn-primary" onclick={handleSubmit} disabled={!isValid || auth.isLoading}>
            {#if auth.isLoading}
                Pairing...
            {:else}
                Pair
            {/if}
        </button>

        <button class="btn-secondary" onclick={handleClear} disabled={auth.isLoading}> Clear</button>
    </div>

    <div class="help">
        <p>The pairing code is shown in the NAS console when it starts.</p>
        <p>Codes expire after 5 minutes.</p>
    </div>
</div>

<style>
    .pairing-form {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
    }

    .header {
        text-align: center;
        margin-bottom: 1.5rem;
    }

    .header h2 {
        margin: 0 0 0.5rem 0;
        font-size: 1.5rem;
        color: #fff;
    }

    .header p {
        margin: 0;
        color: #888;
        font-size: 0.9rem;
    }

    .code-input {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1.5rem;
    }

    .code-input input {
        width: 70px;
        padding: 0.75rem;
        font-size: 1.25rem;
        font-family: monospace;
        text-align: center;
        background: rgba(0, 0, 0, 0.3);
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        color: #fff;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        transition: border-color 0.2s;
    }

    .code-input input:focus {
        outline: none;
        border-color: #4ade80;
    }

    .code-input input:disabled {
        opacity: 0.5;
    }

    .code-input input::placeholder {
        color: rgba(255, 255, 255, 0.3);
    }

    .separator {
        font-size: 1.5rem;
        color: #666;
        font-weight: bold;
    }

    .error {
        padding: 0.75rem;
        margin-bottom: 1rem;
        background: rgba(239, 68, 68, 0.2);
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-radius: 6px;
        color: #fca5a5;
        font-size: 0.9rem;
        text-align: center;
    }

    .actions {
        display: flex;
        gap: 0.75rem;
    }

    .btn-primary,
    .btn-secondary {
        flex: 1;
        padding: 0.75rem;
        border: none;
        border-radius: 8px;
        font-size: 1rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
    }

    .btn-primary {
        background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%);
        color: #000;
    }

    .btn-primary:hover:not(:disabled) {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(74, 222, 128, 0.3);
    }

    .btn-primary:disabled {
        opacity: 0.5;
        cursor: not-allowed;
        transform: none;
    }

    .btn-secondary {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: #e4e4e4;
    }

    .btn-secondary:hover:not(:disabled) {
        background: rgba(255, 255, 255, 0.15);
    }

    .btn-secondary:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .help {
        margin-top: 1.5rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
    }

    .help p {
        margin: 0.25rem 0;
        color: #666;
        font-size: 0.8rem;
    }
</style>