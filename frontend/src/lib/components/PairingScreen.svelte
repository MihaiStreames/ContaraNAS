<script lang="ts">
  import { Card, Stack, Input, Button, Alert } from "$lib/ui";
  import { Server } from "lucide-svelte";

  interface Props {
    onPaired: (nasUrl: string, token: string) => void;
  }

  let { onPaired }: Props = $props();

  // Form state
  let nasUrl = $state("");
  let pairingCode = $state("");

  // Status state
  let status = $state<"idle" | "checking" | "pairing" | "success" | "error">(
    "idle"
  );
  let errorMessage = $state("");

  // Derived states
  const isLoading = $derived(status === "checking" || status === "pairing");
  const canSubmit = $derived(
    nasUrl.trim() !== "" && pairingCode.trim() !== "" && !isLoading
  );

  async function handlePair() {
    if (!canSubmit) return;

    const cleanUrl = nasUrl.trim().replace(/\/$/, "");

    // Step 1: Check if NAS is reachable
    status = "checking";
    errorMessage = "";

    try {
      const healthResponse = await fetch(`${cleanUrl}/api/health`);
      if (!healthResponse.ok) {
        throw new Error("NAS is not reachable");
      }
    } catch {
      status = "error";
      errorMessage =
        "Cannot connect to NAS. Please check the URL and ensure the NAS is running.";
      return;
    }

    // Step 2: Attempt pairing
    status = "pairing";

    try {
      const pairResponse = await fetch(`${cleanUrl}/api/auth/pair`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pairing_code: pairingCode.trim() }),
      });

      if (!pairResponse.ok) {
        const errorData = await pairResponse.json().catch(() => ({}));
        throw new Error(errorData.detail || "Invalid pairing code");
      }

      const data = await pairResponse.json();

      if (data.success && data.api_token) {
        status = "success";
        // Small delay to show success state
        setTimeout(() => {
          onPaired(cleanUrl, data.api_token);
        }, 500);
      } else {
        throw new Error("Pairing failed");
      }
    } catch (e) {
      status = "error";
      errorMessage =
        e instanceof Error ? e.message : "Pairing failed. Please try again.";
    }
  }
</script>

<div class="pairing-screen">
  <div class="pairing-container">
    <Card>
      {#snippet children()}
        <Stack direction="vertical" gap="6">
          <!-- Header -->
          <div class="header">
            <div class="icon-container">
              <Server size={32} />
            </div>
            <h2 class="title">Connect to NAS</h2>
            <p class="subtitle">
              Enter your NAS address and pairing code to connect
            </p>
          </div>

          <!-- Error alert -->
          {#if status === "error" && errorMessage}
            <Alert variant="error" message={errorMessage} />
          {/if}

          <!-- Success alert -->
          {#if status === "success"}
            <Alert
              variant="success"
              message="Paired successfully! Connecting..."
            />
          {/if}

          <!-- Form -->
          <Stack direction="vertical" gap="4">
            <Input
              name="nasUrl"
              label="NAS Address"
              placeholder="http://192.168.1.100:8000"
              bind:value={nasUrl}
              disabled={isLoading}
            />

            <Input
              name="pairingCode"
              label="Pairing Code"
              placeholder="Enter the code shown on your NAS"
              bind:value={pairingCode}
              disabled={isLoading}
            />
          </Stack>

          <!-- Actions -->
          <Button
            label={status === "checking"
              ? "Connecting..."
              : status === "pairing"
                ? "Pairing..."
                : "Connect"}
            variant="primary"
            disabled={!canSubmit}
            loading={isLoading}
            onclick={handlePair}
          />

          <!-- Help text -->
          <p class="help-text">
            Find the pairing code in your NAS terminal or web interface.
          </p>
        </Stack>
      {/snippet}
    </Card>
  </div>
</div>

<style>
  .pairing-screen {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--space-4);
    background: var(--bg-base);
  }

  .pairing-container {
    width: 100%;
    max-width: 420px;
  }

  .header {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: var(--space-2);
  }

  .icon-container {
    width: 64px;
    height: 64px;
    border-radius: var(--radius-full);
    background: var(--color-primary-subtle);
    color: var(--color-primary);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: var(--space-2);
  }

  .title {
    font-size: var(--text-xl);
    font-weight: var(--font-semibold);
    color: var(--text-primary);
    margin: 0;
  }

  .subtitle {
    font-size: var(--text-sm);
    color: var(--text-muted);
    margin: 0;
  }

  .help-text {
    font-size: var(--text-sm);
    color: var(--text-muted);
    text-align: center;
    margin: 0;
  }
</style>
