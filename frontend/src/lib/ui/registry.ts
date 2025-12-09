import type { ComponentType } from "$lib/api";
import type { Component } from "svelte";

// Layout
import Stack from "./layout/Stack.svelte";
import Grid from "./layout/Grid.svelte";

// Card
import Card from "./card/Card.svelte";
import Tile from "./card/Tile.svelte";
import Stat from "./card/Stat.svelte";
import StatCard from "./card/StatCard.svelte";

// Display
import Text from "./display/Text.svelte";
import Badge from "./display/Badge.svelte";
import Progress from "./display/Progress.svelte";
import SegmentedProgress from "./display/SegmentedProgress.svelte";
import LineChart from "./display/LineChart.svelte";
import Image from "./display/Image.svelte";
import Table from "./display/Table.svelte";
import StatSmall from "./display/StatSmall.svelte";

// Interactive
import Button from "./interactive/Button.svelte";
import Input from "./interactive/Input.svelte";
import Select from "./interactive/Select.svelte";
import Toggle from "./interactive/Toggle.svelte";
import Checkbox from "./interactive/Checkbox.svelte";
import Tabs from "./interactive/Tabs.svelte";

// Modal
import Modal from "./modal/Modal.svelte";

// Feedback
import Alert from "./feedback/Alert.svelte";
import Spinner from "./feedback/Spinner.svelte";

/**
 * Registry mapping component type names to Svelte components.
 * Used by ComponentRenderer to dynamically render components from JSON.
 */
export const componentRegistry: Record<ComponentType, Component<any>> = {
  // Layout
  stack: Stack,
  grid: Grid,

  // Card
  card: Card,
  tile: Tile,
  stat: Stat,
  stat_card: StatCard,

  // Display
  text: Text,
  badge: Badge,
  progress: Progress,
  segmented_progress: SegmentedProgress,
  line_chart: LineChart,
  image: Image,
  table: Table,
  stat_small: StatSmall,

  // Interactive
  button: Button,
  input: Input,
  select: Select,
  toggle: Toggle,
  checkbox: Checkbox,
  tabs: Tabs,

  // Modal
  modal: Modal,

  // Feedback
  alert: Alert,
  spinner: Spinner,

  // Helper types (not rendered directly)
  table_column: null as any, // Handled within Table component
  select_option: null as any, // Handled within Select component
  segment: null as any, // Handled within SegmentedProgress component
  tab: null as any, // Handled within Tabs component
};

/**
 * Check if a component type is renderable (has a corresponding Svelte component)
 */
export function isRenderableType(type: ComponentType): boolean {
  return componentRegistry[type] != null;
}
