<script lang="ts">
  import { Stack, Button } from "$lib/ui";
  import { authStore } from "$lib/stores";

  async function handleShutdown() {
    const { invoke } = await import("@tauri-apps/api/core");
    await invoke("exit_app");
  }
</script>

<header class="header">
  <div class="header-content">
    <div class="header-left">
      <h1 class="logo">ContaraNAS</h1>
      <span
        class="connection-indicator"
        class:connected={authStore.connected}
        title={authStore.connected
          ? `Connected to ${authStore.nasUrl}`
          : "Disconnected"}
      ></span>
    </div>
    <Stack direction="horizontal" gap="2" align="center">
      <Button
        variant="ghost"
        size="sm"
        icon="Bell"
        icon_only={true}
        onclick={() => {}}
      />
      <Button
        variant="ghost"
        size="sm"
        icon="FileText"
        icon_only={true}
        onclick={() => {}}
      />
      <Button
        variant="ghost"
        size="sm"
        icon="Power"
        icon_only={true}
        onclick={handleShutdown}
      />
    </Stack>
  </div>
</header>
