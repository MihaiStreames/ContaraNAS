<script lang="ts">
  import "$lib/tokens.css";
  import "$lib/components.css";

  let { children } = $props();
</script>

<div class="app" data-theme="dark">
  {@render children()}
</div>

<style>
  .app {
    min-height: 100vh;
    background: var(--bg-base);
    color: var(--text-primary);
    transition:
      background var(--transition-slow),
      color var(--transition-slow);
  }
</style>
