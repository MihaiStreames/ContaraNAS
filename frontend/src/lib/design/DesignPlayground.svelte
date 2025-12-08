<script lang="ts">
	import { 
		Gamepad2, 
		HardDrive, 
		Container, 
		Database,
		Settings,
		FolderOpen,
		Sun,
		Moon,
		Info,
		CheckCircle,
		AlertTriangle,
		XCircle,
		Plus,
		MoreHorizontal,
		TrendingUp,
		Check,
		X
	} from 'lucide-svelte';
	
	let theme = $state<'light' | 'dark'>('dark');
	
	function toggleTheme() {
		theme = theme === 'light' ? 'dark' : 'light';
	}
	
	// Example data for components
	const stats = [
		{ label: 'Games', value: '127' },
		{ label: 'Libraries', value: '3' },
		{ label: 'Total Size', value: '1.2 TB' },
	];
	
	const tableData = [
		{ name: 'Cyberpunk 2077', size: '65.4 GB', status: 'installed' },
		{ name: 'Elden Ring', size: '44.2 GB', status: 'installed' },
		{ name: 'Baldur\'s Gate 3', size: '122.1 GB', status: 'updating' },
		{ name: 'Hades', size: '15.8 GB', status: 'installed' },
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
			<div class="typography-demo">
				<h1 class="demo-h1">Heading 1</h1>
				<h2 class="demo-h2">Heading 2</h2>
				<h3 class="demo-h3">Heading 3</h3>
				<p class="demo-body">Body text - The quick brown fox jumps over the lazy dog.</p>
				<p class="demo-secondary">Secondary text - Used for descriptions and metadata.</p>
				<p class="demo-muted">Muted text - Less important information.</p>
				<code class="demo-code">monospace code</code>
			</div>
		</section>

		<!-- Cards -->
		<section class="section">
			<h2 class="section-title">Cards</h2>
			<div class="card-grid">
				<!-- Basic Card -->
				<div class="card">
					<div class="card-header">
						<span class="card-icon"><Gamepad2 size={20} strokeWidth={1.75} /></span>
						<h3 class="card-title">Steam</h3>
					</div>
					<div class="card-content">
						<p class="text-secondary">Manage your Steam game library</p>
					</div>
				</div>
				
				<!-- Card with Stats -->
				<div class="card">
					<div class="card-header">
						<span class="card-icon"><Gamepad2 size={20} strokeWidth={1.75} /></span>
						<h3 class="card-title">Steam</h3>
					</div>
					<div class="card-content">
						<div class="stats-row">
							{#each stats as stat}
								<div class="stat">
									<span class="stat-value">{stat.value}</span>
									<span class="stat-label">{stat.label}</span>
								</div>
							{/each}
						</div>
					</div>
					<div class="card-footer">
						<button class="btn btn-ghost btn-sm">View Games</button>
						<button class="btn btn-ghost btn-sm">Libraries</button>
					</div>
				</div>

				<!-- Card with Progress -->
				<div class="card">
					<div class="card-header">
						<span class="card-icon"><HardDrive size={20} strokeWidth={1.75} /></span>
						<h3 class="card-title">Storage</h3>
					</div>
					<div class="card-content">
						<div class="progress-container">
							<div class="progress-header">
								<span class="text-secondary">Drive Usage</span>
								<span class="text-primary font-medium">743 GB / 1 TB</span>
							</div>
							<div class="progress-bar">
								<div class="progress-fill" style="width: 74%"></div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</section>

		<!-- Buttons -->
		<section class="section">
			<h2 class="section-title">Buttons</h2>
			<div class="button-grid">
				<div class="button-row">
					<button class="btn btn-primary">Primary</button>
					<button class="btn btn-secondary">Secondary</button>
					<button class="btn btn-ghost">Ghost</button>
					<button class="btn btn-danger">Danger</button>
				</div>
				<div class="button-row">
					<button class="btn btn-primary btn-sm">Small</button>
					<button class="btn btn-primary">Medium</button>
					<button class="btn btn-primary btn-lg">Large</button>
				</div>
				<div class="button-row">
					<button class="btn btn-primary" disabled>Disabled</button>
					<button class="btn btn-primary btn-loading">
						<span class="spinner"></span>
						Loading
					</button>
					<button class="btn btn-primary btn-icon">
						<Plus size={16} />
						With Icon
					</button>
				</div>
			</div>
		</section>

		<!-- Stats -->
		<section class="section">
			<h2 class="section-title">Stats</h2>
			<div class="stats-grid">
				<div class="stat-card">
					<div class="stat-icon"><Gamepad2 size={24} strokeWidth={1.5} /></div>
					<div class="stat-content">
						<span class="stat-value-lg">127</span>
						<span class="stat-label">Games</span>
					</div>
				</div>
				<div class="stat-card">
					<div class="stat-icon"><Database size={24} strokeWidth={1.5} /></div>
					<div class="stat-content">
						<span class="stat-value-lg">1.2 TB</span>
						<span class="stat-label">Total Size</span>
					</div>
				</div>
				<div class="stat-card stat-success">
					<div class="stat-icon"><CheckCircle size={24} strokeWidth={1.5} /></div>
					<div class="stat-content">
						<span class="stat-value-lg">98%</span>
						<span class="stat-label">Uptime</span>
					</div>
					<div class="stat-trend trend-up"><TrendingUp size={14} /> 2%</div>
				</div>
				<div class="stat-card stat-warning">
					<div class="stat-icon"><AlertTriangle size={24} strokeWidth={1.5} /></div>
					<div class="stat-content">
						<span class="stat-value-lg">3</span>
						<span class="stat-label">Warnings</span>
					</div>
				</div>
			</div>
		</section>

		<!-- Badges -->
		<section class="section">
			<h2 class="section-title">Badges</h2>
			<div class="badge-row">
				<span class="badge">Default</span>
				<span class="badge badge-primary">Primary</span>
				<span class="badge badge-success">Success</span>
				<span class="badge badge-warning">Warning</span>
				<span class="badge badge-error">Error</span>
				<span class="badge badge-info">Info</span>
			</div>
		</section>

		<!-- Form Inputs -->
		<section class="section">
			<h2 class="section-title">Form Inputs</h2>
			<div class="form-grid">
				<div class="form-group">
					<label class="form-label">Text Input</label>
					<input type="text" class="form-input" placeholder="Enter text..." />
				</div>
				<div class="form-group">
					<label class="form-label">Select</label>
					<select class="form-select">
						<option>Option 1</option>
						<option>Option 2</option>
						<option>Option 3</option>
					</select>
				</div>
				<div class="form-group">
					<label class="form-label">Disabled</label>
					<input type="text" class="form-input" placeholder="Disabled..." disabled />
				</div>
				<div class="form-group form-group-inline">
					<label class="toggle">
						<input type="checkbox" checked />
						<span class="toggle-slider"></span>
					</label>
					<span class="form-label">Toggle Switch</span>
				</div>
				<div class="form-group form-group-inline">
					<input type="checkbox" class="checkbox" id="check1" checked />
					<label for="check1">Checkbox</label>
				</div>
			</div>
		</section>

		<!-- Table -->
		<section class="section">
			<h2 class="section-title">Table</h2>
			<div class="table-container">
				<table class="table">
					<thead>
						<tr>
							<th>Game</th>
							<th>Size</th>
							<th>Status</th>
							<th></th>
						</tr>
					</thead>
					<tbody>
						{#each tableData as row}
							<tr>
								<td class="font-medium">{row.name}</td>
								<td class="text-secondary">{row.size}</td>
								<td>
									<span class="badge {row.status === 'updating' ? 'badge-warning' : 'badge-success'}">
										{row.status}
									</span>
								</td>
								<td class="text-right">
									<button class="btn btn-ghost btn-sm btn-icon-only"><MoreHorizontal size={16} /></button>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</section>

		<!-- Alerts -->
		<section class="section">
			<h2 class="section-title">Alerts</h2>
			<div class="alerts-stack">
				<div class="alert alert-info">
					<span class="alert-icon"><Info size={14} /></span>
					<div class="alert-content">
						<strong>Info:</strong> This is an informational message.
					</div>
				</div>
				<div class="alert alert-success">
					<span class="alert-icon"><Check size={14} /></span>
					<div class="alert-content">
						<strong>Success:</strong> Operation completed successfully.
					</div>
				</div>
				<div class="alert alert-warning">
					<span class="alert-icon"><AlertTriangle size={14} /></span>
					<div class="alert-content">
						<strong>Warning:</strong> Please review before proceeding.
					</div>
				</div>
				<div class="alert alert-error">
					<span class="alert-icon"><X size={14} /></span>
					<div class="alert-content">
						<strong>Error:</strong> Something went wrong.
					</div>
				</div>
			</div>
		</section>

		<!-- Modal Preview -->
		<section class="section">
			<h2 class="section-title">Modal (Preview)</h2>
			<div class="modal-preview">
				<div class="modal">
					<div class="modal-header">
						<h3 class="modal-title">Installed Games</h3>
						<button class="modal-close"><X size={18} /></button>
					</div>
					<div class="modal-body">
						<p class="text-secondary">This is a modal dialog for showing detailed content.</p>
					</div>
					<div class="modal-footer">
						<button class="btn btn-ghost">Cancel</button>
						<button class="btn btn-primary">Confirm</button>
					</div>
				</div>
			</div>
		</section>

		<!-- Example Module Tile -->
		<section class="section">
			<h2 class="section-title">Example Module Tile</h2>
			<div class="tiles-grid">
				<!-- Steam Module -->
				<div class="module-tile">
					<div class="tile-header">
						<div class="tile-icon"><Gamepad2 size={22} strokeWidth={1.75} /></div>
						<div class="tile-title-group">
							<h3 class="tile-title">Steam</h3>
							<span class="badge badge-success">Running</span>
						</div>
					</div>
					<div class="tile-stats">
						<div class="tile-stat">
							<span class="tile-stat-value">127</span>
							<span class="tile-stat-label">Games</span>
						</div>
						<div class="tile-stat">
							<span class="tile-stat-value">3</span>
							<span class="tile-stat-label">Libraries</span>
						</div>
						<div class="tile-stat">
							<span class="tile-stat-value">1.2 TB</span>
							<span class="tile-stat-label">Size</span>
						</div>
					</div>
					<div class="tile-actions">
						<button class="btn btn-ghost btn-sm">View Games</button>
						<button class="btn btn-ghost btn-sm btn-icon-only"><Settings size={16} /></button>
					</div>
				</div>

				<!-- Docker Module -->
				<div class="module-tile">
					<div class="tile-header">
						<div class="tile-icon"><Container size={22} strokeWidth={1.75} /></div>
						<div class="tile-title-group">
							<h3 class="tile-title">Docker</h3>
							<span class="badge badge-success">Running</span>
						</div>
					</div>
					<div class="tile-stats">
						<div class="tile-stat">
							<span class="tile-stat-value">12</span>
							<span class="tile-stat-label">Containers</span>
						</div>
						<div class="tile-stat">
							<span class="tile-stat-value">8</span>
							<span class="tile-stat-label">Running</span>
						</div>
						<div class="tile-stat">
							<span class="tile-stat-value">45 GB</span>
							<span class="tile-stat-label">Images</span>
						</div>
					</div>
					<div class="tile-actions">
						<button class="btn btn-ghost btn-sm">Containers</button>
						<button class="btn btn-ghost btn-sm btn-icon-only"><Settings size={16} /></button>
					</div>
				</div>

				<!-- Storage Module -->
				<div class="module-tile">
					<div class="tile-header">
						<div class="tile-icon"><HardDrive size={22} strokeWidth={1.75} /></div>
						<div class="tile-title-group">
							<h3 class="tile-title">Storage</h3>
							<span class="badge badge-warning">74% Used</span>
						</div>
					</div>
					<div class="tile-content">
						<div class="progress-container">
							<div class="progress-bar progress-bar-lg">
								<div class="progress-fill progress-warning" style="width: 74%"></div>
							</div>
							<div class="progress-labels">
								<span class="text-muted">743 GB used</span>
								<span class="text-muted">1 TB total</span>
							</div>
						</div>
					</div>
					<div class="tile-actions">
						<button class="btn btn-ghost btn-sm">Manage</button>
						<button class="btn btn-ghost btn-sm btn-icon-only"><Settings size={16} /></button>
					</div>
				</div>
			</div>
		</section>
	</main>
</div>

<style>
	@import './tokens.css';

	/* ========================================
	   Playground Layout
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
	   Colors
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
	   Typography
	   ======================================== */
	
	.typography-demo {
		display: flex;
		flex-direction: column;
		gap: var(--space-3);
	}
	
	.demo-h1 { font-size: var(--text-3xl); font-weight: var(--font-bold); }
	.demo-h2 { font-size: var(--text-2xl); font-weight: var(--font-semibold); }
	.demo-h3 { font-size: var(--text-xl); font-weight: var(--font-medium); }
	.demo-body { font-size: var(--text-base); }
	.demo-secondary { font-size: var(--text-sm); color: var(--text-secondary); }
	.demo-muted { font-size: var(--text-sm); color: var(--text-muted); }
	.demo-code { 
		font-family: var(--font-mono); 
		font-size: var(--text-sm);
		background: var(--bg-surface-2);
		padding: var(--space-1) var(--space-2);
		border-radius: var(--radius-sm);
	}


	/* ========================================
	   Cards
	   ======================================== */
	
	.card-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
		gap: var(--space-4);
	}
	
	.card {
		background: var(--bg-surface-1);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-lg);
		box-shadow: var(--shadow-md);
		overflow: hidden;
	}
	
	[data-theme="dark"] .card {
		box-shadow: var(--shadow-md), var(--edge-highlight);
	}
	
	.card-header {
		display: flex;
		align-items: center;
		gap: var(--space-3);
		padding: var(--space-4);
		border-bottom: 1px solid var(--border-subtle);
	}
	
	.card-icon {
		display: flex;
		align-items: center;
		justify-content: center;
		color: var(--text-secondary);
	}
	
	.card-title {
		font-size: var(--text-base);
		font-weight: var(--font-semibold);
	}
	
	.card-content {
		padding: var(--space-4);
	}
	
	.card-footer {
		display: flex;
		gap: var(--space-2);
		padding: var(--space-3) var(--space-4);
		border-top: 1px solid var(--border-subtle);
		background: var(--bg-surface-2);
	}


	/* ========================================
	   Stats
	   ======================================== */
	
	.stats-row {
		display: flex;
		gap: var(--space-6);
	}
	
	.stat {
		display: flex;
		flex-direction: column;
	}
	
	.stat-value {
		font-size: var(--text-xl);
		font-weight: var(--font-semibold);
	}
	
	.stat-label {
		font-size: var(--text-sm);
		color: var(--text-muted);
	}
	
	.stats-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
		gap: var(--space-4);
	}
	
	.stat-card {
		display: flex;
		align-items: center;
		gap: var(--space-3);
		padding: var(--space-4);
		background: var(--bg-surface-1);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-lg);
		box-shadow: var(--shadow-sm);
	}
	
	.stat-card.stat-success { border-left: 3px solid var(--color-success); }
	.stat-card.stat-warning { border-left: 3px solid var(--color-warning); }
	.stat-card.stat-error { border-left: 3px solid var(--color-error); }
	
	.stat-icon {
		display: flex;
		align-items: center;
		justify-content: center;
		color: var(--text-secondary);
	}
	
	.stat-content {
		flex: 1;
		display: flex;
		flex-direction: column;
	}
	
	.stat-value-lg {
		font-size: var(--text-xl);
		font-weight: var(--font-bold);
	}
	
	.stat-trend {
		display: flex;
		align-items: center;
		gap: var(--space-1);
		font-size: var(--text-sm);
		font-weight: var(--font-medium);
	}
	
	.trend-up { color: var(--color-success); }
	.trend-down { color: var(--color-error); }


	/* ========================================
	   Progress
	   ======================================== */
	
	.progress-container {
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
	}
	
	.progress-header {
		display: flex;
		justify-content: space-between;
		font-size: var(--text-sm);
	}
	
	.progress-bar {
		height: 8px;
		background: var(--bg-surface-3);
		border-radius: var(--radius-full);
		overflow: hidden;
	}
	
	.progress-bar-lg {
		height: 12px;
	}
	
	.progress-fill {
		height: 100%;
		background: var(--color-primary);
		border-radius: var(--radius-full);
		transition: width var(--transition-slow);
	}
	
	.progress-fill.progress-warning {
		background: var(--color-warning);
	}
	
	.progress-labels {
		display: flex;
		justify-content: space-between;
		font-size: var(--text-xs);
	}


	/* ========================================
	   Buttons
	   ======================================== */
	
	.button-grid {
		display: flex;
		flex-direction: column;
		gap: var(--space-4);
	}
	
	.button-row {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-3);
		align-items: center;
	}
	
	.btn {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: var(--space-2);
		padding: var(--space-2) var(--space-4);
		font-size: var(--text-sm);
		font-weight: var(--font-medium);
		border-radius: var(--radius-md);
		border: none;
		cursor: pointer;
		transition: all var(--transition-base);
		white-space: nowrap;
	}
	
	.btn:focus-visible {
		outline: none;
		box-shadow: var(--glow-primary);
	}
	
	.btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}
	
	/* Primary */
	.btn-primary {
		background: var(--color-primary);
		color: var(--text-inverse);
	}
	
	.btn-primary:hover:not(:disabled) {
		background: var(--color-primary-hover);
	}
	
	.btn-primary:active:not(:disabled) {
		background: var(--color-primary-active);
	}
	
	/* Secondary */
	.btn-secondary {
		background: var(--bg-surface-2);
		color: var(--text-primary);
		border: 1px solid var(--border-default);
	}
	
	.btn-secondary:hover:not(:disabled) {
		background: var(--bg-surface-3);
		border-color: var(--border-strong);
	}
	
	/* Ghost */
	.btn-ghost {
		background: transparent;
		color: var(--text-secondary);
	}
	
	.btn-ghost:hover:not(:disabled) {
		background: var(--hover-overlay);
		color: var(--text-primary);
	}
	
	/* Danger */
	.btn-danger {
		background: var(--color-error);
		color: white;
	}
	
	.btn-danger:hover:not(:disabled) {
		background: #dc2626;
	}
	
	/* Sizes */
	.btn-sm {
		padding: var(--space-1) var(--space-3);
		font-size: var(--text-xs);
	}
	
	.btn-lg {
		padding: var(--space-3) var(--space-6);
		font-size: var(--text-base);
	}
	
	/* Icon only */
	.btn-icon-only {
		padding: var(--space-2);
		aspect-ratio: 1;
	}
	
	/* Loading */
	.btn-loading {
		position: relative;
		pointer-events: none;
	}
	
	.spinner {
		width: 14px;
		height: 14px;
		border: 2px solid transparent;
		border-top-color: currentColor;
		border-radius: 50%;
		animation: spin 0.6s linear infinite;
	}
	
	@keyframes spin {
		to { transform: rotate(360deg); }
	}


	/* ========================================
	   Badges
	   ======================================== */
	
	.badge-row {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-2);
	}
	
	.badge {
		display: inline-flex;
		align-items: center;
		padding: var(--space-1) var(--space-2);
		font-size: var(--text-xs);
		font-weight: var(--font-medium);
		border-radius: var(--radius-full);
		background: var(--bg-surface-3);
		color: var(--text-secondary);
	}
	
	.badge-primary {
		background: var(--color-primary-subtle);
		color: var(--color-primary);
	}
	
	.badge-success {
		background: var(--color-success-subtle);
		color: var(--color-success-text);
	}
	
	.badge-warning {
		background: var(--color-warning-subtle);
		color: var(--color-warning-text);
	}
	
	.badge-error {
		background: var(--color-error-subtle);
		color: var(--color-error-text);
	}
	
	.badge-info {
		background: var(--color-info-subtle);
		color: var(--color-info-text);
	}


	/* ========================================
	   Form Inputs
	   ======================================== */
	
	.form-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
		gap: var(--space-4);
	}
	
	.form-group {
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
	}
	
	.form-group-inline {
		flex-direction: row;
		align-items: center;
	}
	
	.form-label {
		font-size: var(--text-sm);
		font-weight: var(--font-medium);
		color: var(--text-secondary);
	}
	
	.form-input,
	.form-select {
		padding: var(--space-2) var(--space-3);
		font-size: var(--text-sm);
		background: var(--bg-surface-1);
		border: 1px solid var(--border-default);
		border-radius: var(--radius-md);
		color: var(--text-primary);
		transition: all var(--transition-base);
	}
	
	.form-input:focus,
	.form-select:focus {
		outline: none;
		border-color: var(--color-primary);
		box-shadow: var(--glow-primary);
	}
	
	.form-input:disabled {
		background: var(--bg-surface-2);
		color: var(--text-muted);
		cursor: not-allowed;
	}
	
	.form-input::placeholder {
		color: var(--text-muted);
	}
	
	/* Toggle Switch */
	.toggle {
		position: relative;
		display: inline-block;
		width: 44px;
		height: 24px;
	}
	
	.toggle input {
		opacity: 0;
		width: 0;
		height: 0;
	}
	
	.toggle-slider {
		position: absolute;
		cursor: pointer;
		inset: 0;
		background: var(--bg-surface-3);
		border-radius: var(--radius-full);
		transition: var(--transition-base);
	}
	
	.toggle-slider::before {
		position: absolute;
		content: "";
		height: 18px;
		width: 18px;
		left: 3px;
		bottom: 3px;
		background: white;
		border-radius: 50%;
		transition: var(--transition-base);
		box-shadow: var(--shadow-sm);
	}
	
	.toggle input:checked + .toggle-slider {
		background: var(--color-primary);
	}
	
	.toggle input:checked + .toggle-slider::before {
		transform: translateX(20px);
	}
	
	/* Checkbox */
	.checkbox {
		width: 18px;
		height: 18px;
		accent-color: var(--color-primary);
	}


	/* ========================================
	   Table
	   ======================================== */
	
	.table-container {
		overflow-x: auto;
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-lg);
	}
	
	.table {
		width: 100%;
		border-collapse: collapse;
		font-size: var(--text-sm);
	}
	
	.table th,
	.table td {
		padding: var(--space-3) var(--space-4);
		text-align: left;
	}
	
	.table th {
		background: var(--bg-surface-2);
		font-weight: var(--font-medium);
		color: var(--text-secondary);
		border-bottom: 1px solid var(--border-default);
	}
	
	.table td {
		background: var(--bg-surface-1);
		border-bottom: 1px solid var(--border-subtle);
	}
	
	.table tr:last-child td {
		border-bottom: none;
	}
	
	.table tr:hover td {
		background: var(--hover-overlay);
	}
	
	.text-right {
		text-align: right;
	}


	/* ========================================
	   Alerts
	   ======================================== */
	
	.alerts-stack {
		display: flex;
		flex-direction: column;
		gap: var(--space-3);
	}
	
	.alert {
		display: flex;
		align-items: flex-start;
		gap: var(--space-3);
		padding: var(--space-3) var(--space-4);
		border-radius: var(--radius-md);
		font-size: var(--text-sm);
	}
	
	.alert-info {
		background: var(--color-info-subtle);
		color: var(--color-info-text);
	}
	
	.alert-success {
		background: var(--color-success-subtle);
		color: var(--color-success-text);
	}
	
	.alert-warning {
		background: var(--color-warning-subtle);
		color: var(--color-warning-text);
	}
	
	.alert-error {
		background: var(--color-error-subtle);
		color: var(--color-error-text);
	}
	
	.alert-icon {
		flex-shrink: 0;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	
	.alert-info .alert-icon {
		color: var(--color-info);
	}
	
	.alert-success .alert-icon {
		color: var(--color-success);
	}
	
	.alert-warning .alert-icon {
		color: var(--color-warning);
	}
	
	.alert-error .alert-icon {
		color: var(--color-error);
	}


	/* ========================================
	   Modal
	   ======================================== */
	
	.modal-preview {
		background: var(--bg-base);
		padding: var(--space-8);
		border-radius: var(--radius-lg);
		border: 1px solid var(--border-subtle);
		display: flex;
		justify-content: center;
	}
	
	.modal {
		width: 100%;
		max-width: 400px;
		background: var(--bg-surface-1);
		border-radius: var(--radius-xl);
		box-shadow: var(--shadow-xl);
		overflow: hidden;
	}
	
	[data-theme="dark"] .modal {
		box-shadow: var(--shadow-xl), var(--edge-highlight);
	}
	
	.modal-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: var(--space-4);
		border-bottom: 1px solid var(--border-subtle);
	}
	
	.modal-title {
		font-size: var(--text-lg);
		font-weight: var(--font-semibold);
	}
	
	.modal-close {
		width: 32px;
		height: 32px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: transparent;
		border: none;
		border-radius: var(--radius-md);
		color: var(--text-muted);
		cursor: pointer;
		transition: all var(--transition-base);
	}
	
	.modal-close:hover {
		background: var(--hover-overlay);
		color: var(--text-primary);
	}
	
	.modal-body {
		padding: var(--space-4);
	}
	
	.modal-footer {
		display: flex;
		justify-content: flex-end;
		gap: var(--space-2);
		padding: var(--space-4);
		border-top: 1px solid var(--border-subtle);
		background: var(--bg-surface-2);
	}


	/* ========================================
	   Module Tiles
	   ======================================== */
	
	.tiles-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
		gap: var(--space-4);
	}
	
	.module-tile {
		background: var(--bg-surface-1);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-xl);
		box-shadow: var(--shadow-md);
		overflow: hidden;
		transition: all var(--transition-base);
	}
	
	[data-theme="dark"] .module-tile {
		box-shadow: var(--shadow-md), var(--edge-highlight);
	}
	
	.module-tile:hover {
		box-shadow: var(--shadow-lg);
		border-color: var(--border-default);
	}
	
	.tile-header {
		display: flex;
		align-items: center;
		gap: var(--space-3);
		padding: var(--space-4);
	}
	
	.tile-icon {
		width: 40px;
		height: 40px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--bg-surface-2);
		border-radius: var(--radius-md);
		color: var(--text-secondary);
	}
	
	.tile-title-group {
		flex: 1;
		display: flex;
		align-items: center;
		gap: var(--space-2);
	}
	
	.tile-title {
		font-size: var(--text-base);
		font-weight: var(--font-semibold);
	}
	
	.tile-stats {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: var(--space-2);
		padding: 0 var(--space-4) var(--space-4);
	}
	
	.tile-stat {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: var(--space-3);
		background: var(--bg-surface-2);
		border-radius: var(--radius-md);
	}
	
	.tile-stat-value {
		font-size: var(--text-lg);
		font-weight: var(--font-bold);
		color: var(--text-primary);
	}
	
	.tile-stat-label {
		font-size: var(--text-xs);
		color: var(--text-muted);
	}
	
	.tile-content {
		padding: 0 var(--space-4) var(--space-4);
	}
	
	.tile-actions {
		display: flex;
		justify-content: space-between;
		padding: var(--space-3) var(--space-4);
		border-top: 1px solid var(--border-subtle);
		background: var(--bg-surface-2);
	}


	/* ========================================
	   Utilities
	   ======================================== */
	
	.text-primary { color: var(--text-primary); }
	.text-secondary { color: var(--text-secondary); }
	.text-muted { color: var(--text-muted); }
	.font-medium { font-weight: var(--font-medium); }
	.font-bold { font-weight: var(--font-bold); }
</style>