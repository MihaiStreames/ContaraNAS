<script lang="ts">
  import type { ComponentSchema, ActionRef } from "$lib/api";
  import { setActionContext } from "$lib/context";
  import ComponentRenderer from "./ComponentRenderer.svelte";

  interface Props {
    moduleName: string;
    component: ComponentSchema;
    onAction: (moduleName: string, actionRef: ActionRef) => Promise<void>;
  }

  let { moduleName, component, onAction }: Props = $props();

  // Set up action context for this module's component tree
  setActionContext({
    moduleName,
    handleAction: (actionRef) => onAction(moduleName, actionRef),
  });
</script>

<ComponentRenderer {component} />
