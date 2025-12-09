<script lang="ts">
  import { PairingScreen, Dashboard } from "$lib/components";
  import { authStore } from "$lib/stores";
  import { onMount } from "svelte";

  // View state
  let view = $state<"loading" | "pairing" | "dashboard">("loading");

  onMount(() => {
    // Check if we have stored credentials
    if (authStore.hasCredentials) {
      view = "dashboard";
    } else {
      view = "pairing";
    }
  });

  function handlePaired(nasUrl: string, token: string) {
    authStore.setCredentials(token, nasUrl);
    view = "dashboard";
  }

  function handleDisconnect() {
    view = "pairing";
  }
</script>

{#if view === "loading"}
  <div class="loading-screen">
    <div class="loader"></div>
  </div>
{:else if view === "pairing"}
  <PairingScreen onPaired={handlePaired} />
{:else if view === "dashboard"}
  <Dashboard onDisconnect={handleDisconnect} />
{/if}

<style>
  .loading-screen {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-base);
  }

  .loader {
    width: 40px;
    height: 40px;
    border: 3px solid var(--border-subtle);
    border-top-color: var(--color-primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
</style>
