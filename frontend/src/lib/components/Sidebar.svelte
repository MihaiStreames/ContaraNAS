<script lang="ts">
  import { Icon } from "$lib/ui";

  interface NavItem {
    id: string;
    label: string;
    icon: string;
    href?: string;
  }

  interface Props {
    items?: NavItem[];
    active?: string;
    onNavigate?: (id: string) => void;
  }

  let {
    items = [
      { id: "dashboard", label: "Dashboard", icon: "LayoutDashboard" },
      { id: "marketplace", label: "Marketplace", icon: "Store" },
      { id: "settings", label: "Settings", icon: "Settings" },
    ],
    active = "dashboard",
    onNavigate,
  }: Props = $props();

  function handleClick(id: string) {
    if (onNavigate) {
      onNavigate(id);
    }
  }
</script>

<aside class="sidebar">
  <nav class="sidebar-nav">
    {#each items as item}
      <button
        class="sidebar-item"
        class:active={active === item.id}
        onclick={() => handleClick(item.id)}
      >
        <span class="sidebar-label">{item.label}</span>
        <Icon name={item.icon} size={18} />
      </button>
    {/each}
  </nav>
</aside>
