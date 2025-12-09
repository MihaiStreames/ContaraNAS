<script lang="ts">
	import { Sun, Moon } from 'lucide-svelte';

	// Import UI components
	import {
		Stack,
		Grid,
		Card,
		Tile,
		Stat,
		StatCard,
		Text,
		Badge,
		Progress,
		Table,
		Button,
		Input,
		Select,
		Toggle,
		Checkbox,
		Modal,
		Alert,
		Spinner
	} from '$lib/ui';

	let theme = $state<'light' | 'dark'>('dark');
	let modalOpen = $state(false);

	function toggleTheme() {
		theme = theme === 'light' ? 'dark' : 'light';
		// Update the app wrapper theme
		document.querySelector('.app')?.setAttribute('data-theme', theme);
	}

	// Example data
	const stats = [
		{ type: 'stat' as const, label: 'Games', value: '127' },
		{ type: 'stat' as const, label: 'Libraries', value: '3' },
		{ type: 'stat' as const, label: 'Total Size', value: '1.2 TB' }
	];

	const tableColumns = [
		{ type: 'table_column' as const, key: 'name', label: 'Game' },
		{ type: 'table_column' as const, key: 'size', label: 'Size' },
		{ type: 'table_column' as const, key: 'status', label: 'Status' },
		{ type: 'table_column' as const, key: 'actions', label: '', align: 'right' as const }
	];

	const tableData = [
		{ name: 'Cyberpunk 2077', size: '65.4 GB', status: 'installed' },
		{ name: 'Elden Ring', size: '44.2 GB', status: 'installed' },
		{ name: "Baldur's Gate 3", size: '122.1 GB', status: 'updating' },
		{ name: 'Hades', size: '15.8 GB', status: 'installed' }
	];

	const selectOptions = [
		{ type: 'select_option' as const, value: '1', label: 'Option 1' },
		{ type: 'select_option' as const, value: '2', label: 'Option 2' },
		{ type: 'select_option' as const, value: '3', label: 'Option 3' }
	];
</script>

<div class="playground" data-theme={theme}>
	<!-- Header -->
	<header class="header">
		<h1>ContaraNAS Design System</h1>
		<button class="theme-toggle" onclick={toggleTheme}>
			{#if theme === 'light'}
				<Moon size={16} />
				<span>Dark</span>
			{:else}
				<Sun size={16} />
				<span>Light</span>
			{/if}
		</button>
	</header>

	<main class="content">
		<!-- Color Palette -->
		<section class="section">
			<h2 class="section-title">Colors</h2>
			<div class="color-grid">
				<div class="color-swatch">
					<div class="swatch" style="background: var(--bg-base)"></div>
					<span>bg-base</span>
				</div>
				<div class="color-swatch">
					<div class="swatch" style="background: var(--bg-surface-1)"></div>
					<span>surface-1</span>
				</div>
				<div class="color-swatch">
					<div class="swatch" style="background: var(--bg-surface-2)"></div>
					<span>surface-2</span>
				</div>
				<div class="color-swatch">
					<div class="swatch" style="background: var(--bg-surface-3)"></div>
					<span>surface-3</span>
				</div>
				<div class="color-swatch">
					<div class="swatch" style="background: var(--color-primary)"></div>
					<span>primary</span>
				</div>
				<div class="color-swatch">
					<div class="swatch" style="background: var(--color-success)"></div>
					<span>success</span>
				</div>
				<div class="color-swatch">
					<div class="swatch" style="background: var(--color-warning)"></div>
					<span>warning</span>
				</div>
				<div class="color-swatch">
					<div class="swatch" style="background: var(--color-error)"></div>
					<span>error</span>
				</div>
			</div>
		</section>

		<!-- Typography -->
		<section class="section">
			<h2 class="section-title">Typography</h2>
			<Stack gap="3">
				<h1 class="demo-h1">Heading 1</h1>
				<h2 class="demo-h2">Heading 2</h2>
				<h3 class="demo-h3">Heading 3</h3>
				<Text content="Body text - The quick brown fox jumps over the lazy dog." />
				<Text content="Secondary text - Used for descriptions and metadata." variant="secondary" />
				<Text content="Muted text - Less important information." variant="muted" />
				<Text content="monospace code" variant="code" />
			</Stack>
		</section>

		<!-- Cards -->
		<section class="section">
			<h2 class="section-title">Cards</h2>
			<Grid columns="repeat(auto-fill, minmax(300px, 1fr))" gap="4">
				<!-- Basic Card -->
				<Card icon="Gamepad2" title="Steam">
					<Text content="Manage your Steam game library" variant="secondary" />
				</Card>

				<!-- Card with Stats -->
				<Card icon="Gamepad2" title="Steam">
					{#snippet children()}
						<Stack direction="horizontal" gap="6">
							{#each stats as stat}
								<Stat label={stat.label} value={stat.value} />
							{/each}
						</Stack>
					{/snippet}
					{#snippet footer()}
						<Button label="View Games" variant="ghost" size="sm" />
						<Button label="Libraries" variant="ghost" size="sm" />
					{/snippet}
				</Card>

				<!-- Card with Progress -->
				<Card icon="HardDrive" title="Storage">
					<Progress value={74} label="Drive Usage" sublabel="743 GB / 1 TB" />
				</Card>
			</Grid>
		</section>

		<!-- Buttons -->
		<section class="section">
			<h2 class="section-title">Buttons</h2>
			<Stack gap="4">
				<Stack direction="horizontal" gap="3">
					<Button label="Primary" variant="primary" />
					<Button label="Secondary" variant="secondary" />
					<Button label="Ghost" variant="ghost" />
					<Button label="Danger" variant="danger" />
				</Stack>
				<Stack direction="horizontal" gap="3" align="center">
					<Button label="Small" variant="primary" size="sm" />
					<Button label="Medium" variant="primary" size="md" />
					<Button label="Large" variant="primary" size="lg" />
				</Stack>
				<Stack direction="horizontal" gap="3" align="center">
					<Button label="Disabled" variant="primary" disabled />
					<Button label="Loading" variant="primary" loading />
					<Button label="With Icon" variant="primary" icon="Plus" />
				</Stack>
			</Stack>
		</section>

		<!-- Stats -->
		<section class="section">
			<h2 class="section-title">Stats</h2>
			<Grid columns="repeat(auto-fill, minmax(180px, 1fr))" gap="4">
				<StatCard label="Games" value="127" icon="Gamepad2" />
				<StatCard label="Total Size" value="1.2 TB" icon="Database" />
				<StatCard label="Uptime" value="98%" icon="CheckCircle" color="success" trend={['up', '2%']} />
				<StatCard label="Warnings" value="3" icon="AlertTriangle" color="warning" />
			</Grid>
		</section>

		<!-- Badges -->
		<section class="section">
			<h2 class="section-title">Badges</h2>
			<Stack direction="horizontal" gap="2">
				<Badge text="Default" />
				<Badge text="Primary" variant="primary" />
				<Badge text="Success" variant="success" />
				<Badge text="Warning" variant="warning" />
				<Badge text="Error" variant="error" />
				<Badge text="Info" variant="info" />
			</Stack>
		</section>

		<!-- Form Inputs -->
		<section class="section">
			<h2 class="section-title">Form Inputs</h2>
			<Grid columns="repeat(auto-fill, minmax(250px, 1fr))" gap="4">
				<Input name="text" label="Text Input" placeholder="Enter text..." />
				<Select name="select" label="Select" options={selectOptions} value="1" />
				<Input name="disabled" label="Disabled" placeholder="Disabled..." disabled />
				<Toggle name="toggle" label="Toggle Switch" checked />
				<Checkbox name="checkbox" label="Checkbox" checked />
			</Grid>
		</section>

		<!-- Table -->
		<section class="section">
			<h2 class="section-title">Table</h2>
			<Table columns={tableColumns} data={tableData} />
		</section>

		<!-- Alerts -->
		<section class="section">
			<h2 class="section-title">Alerts</h2>
			<Stack gap="3">
				<Alert variant="info" title="Info" message="This is an informational message." />
				<Alert variant="success" title="Success" message="Operation completed successfully." />
				<Alert variant="warning" title="Warning" message="Please review before proceeding." />
				<Alert variant="error" title="Error" message="Something went wrong." />
			</Stack>
		</section>

		<!-- Spinner -->
		<section class="section">
			<h2 class="section-title">Spinners</h2>
			<Stack direction="horizontal" gap="4" align="center">
				<Spinner size="sm" />
				<Spinner size="md" />
				<Spinner size="lg" />
				<Spinner size="md" label="Loading..." />
			</Stack>
		</section>

		<!-- Modal -->
		<section class="section">
			<h2 class="section-title">Modal</h2>
			<Button label="Open Modal" variant="primary" onclick={() => (modalOpen = true)} />

			<Modal id="demo-modal" title="Installed Games" open={modalOpen} onclose={() => (modalOpen = false)}>
				{#snippet children()}
					<Text content="This is a modal dialog for showing detailed content." variant="secondary" />
				{/snippet}
				{#snippet footer()}
					<Button label="Cancel" variant="ghost" onclick={() => (modalOpen = false)} />
					<Button label="Confirm" variant="primary" onclick={() => (modalOpen = false)} />
				{/snippet}
			</Modal>
		</section>

		<!-- Example Module Tiles -->
		<section class="section">
			<h2 class="section-title">Example Module Tiles</h2>
			<Grid columns="repeat(auto-fill, minmax(320px, 1fr))" gap="4">
				<!-- Steam Module -->
				<Tile
					icon="Gamepad2"
					title="Steam"
					badge={{ type: 'badge', text: 'Running', variant: 'success' }}
					stats={[
						{ type: 'stat', label: 'Games', value: '127' },
						{ type: 'stat', label: 'Libraries', value: '3' },
						{ type: 'stat', label: 'Size', value: '1.2 TB' }
					]}
				>
					{#snippet actions()}
						<Button label="View Games" variant="ghost" size="sm" />
						<Button icon="Settings" variant="ghost" size="sm" icon_only />
					{/snippet}
				</Tile>

				<!-- Docker Module -->
				<Tile
					icon="Container"
					title="Docker"
					badge={{ type: 'badge', text: 'Running', variant: 'success' }}
					stats={[
						{ type: 'stat', label: 'Containers', value: '12' },
						{ type: 'stat', label: 'Running', value: '8' },
						{ type: 'stat', label: 'Images', value: '45 GB' }
					]}
				>
					{#snippet actions()}
						<Button label="Containers" variant="ghost" size="sm" />
						<Button icon="Settings" variant="ghost" size="sm" icon_only />
					{/snippet}
				</Tile>

				<!-- Storage Module -->
				<Tile
					icon="HardDrive"
					title="Storage"
					badge={{ type: 'badge', text: '74% Used', variant: 'warning' }}
				>
					{#snippet content()}
						<Stack gap="2">
							<Progress value={74} max={100} size="lg" color="warning" />
							<Stack direction="horizontal" justify="between">
								<Text content="743 GB used" variant="muted" />
								<Text content="1 TB total" variant="muted" />
							</Stack>
						</Stack>
					{/snippet}
					{#snippet actions()}
						<Button label="Manage" variant="ghost" size="sm" />
						<Button icon="Settings" variant="ghost" size="sm" icon_only />
					{/snippet}
				</Tile>
			</Grid>
		</section>
	</main>
</div>

<style>
	/* ========================================
	   Playground Layout (minimal - page-specific styles only)
	   ======================================== */

	.playground {
		min-height: 100vh;
		background: var(--bg-base);
		color: var(--text-primary);
		transition: background var(--transition-slow), color var(--transition-slow);
	}

	.header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: var(--space-4) var(--space-6);
		background: var(--bg-surface-1);
		border-bottom: 1px solid var(--border-subtle);
		position: sticky;
		top: 0;
		z-index: 10;
	}

	.header h1 {
		font-size: var(--text-xl);
		font-weight: var(--font-semibold);
	}

	.theme-toggle {
		display: flex;
		align-items: center;
		gap: var(--space-2);
		padding: var(--space-2) var(--space-4);
		background: var(--bg-surface-2);
		border: 1px solid var(--border-default);
		border-radius: var(--radius-md);
		color: var(--text-primary);
		cursor: pointer;
		font-size: var(--text-sm);
		transition: all var(--transition-base);
	}

	.theme-toggle:hover {
		background: var(--bg-surface-3);
	}

	.content {
		max-width: 1200px;
		margin: 0 auto;
		padding: var(--space-8);
	}

	.section {
		margin-bottom: var(--space-12);
	}

	.section-title {
		font-size: var(--text-lg);
		font-weight: var(--font-semibold);
		margin-bottom: var(--space-4);
		padding-bottom: var(--space-2);
		border-bottom: 1px solid var(--border-subtle);
		color: var(--text-secondary);
	}

	/* ========================================
	   Colors Section
	   ======================================== */

	.color-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
		gap: var(--space-4);
	}

	.color-swatch {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: var(--space-2);
	}

	.swatch {
		width: 60px;
		height: 60px;
		border-radius: var(--radius-md);
		border: 1px solid var(--border-default);
		box-shadow: var(--shadow-sm);
	}

	.color-swatch span {
		font-size: var(--text-xs);
		color: var(--text-muted);
	}

	/* ========================================
	   Typography Demo
	   ======================================== */

	.demo-h1 {
		font-size: var(--text-3xl);
		font-weight: var(--font-bold);
	}
	.demo-h2 {
		font-size: var(--text-2xl);
		font-weight: var(--font-semibold);
	}
	.demo-h3 {
		font-size: var(--text-xl);
		font-weight: var(--font-medium);
	}
</style>
