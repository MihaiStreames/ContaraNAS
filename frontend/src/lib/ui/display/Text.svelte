<script lang="ts">
  import type { TextSchema } from "$lib/api";

  interface Props extends Partial<Omit<TextSchema, "type">> {}

  let { content = "", variant = "body", size = "base" }: Props = $props();
</script>

{#if variant === "code"}
  <code class="text-code text-size-{size}">{content}</code>
{:else}
  <span class="text-{variant} text-size-{size}">{content}</span>
{/if}
