/**
 * Action context for wiring up button clicks to module actions
 */

import { getContext, setContext } from "svelte";
import type { ActionRef } from "$lib/api";

const ACTION_CONTEXT_KEY = Symbol("action-context");

export interface ActionContext {
  moduleName: string;
  handleAction: (actionRef: ActionRef) => Promise<void>;
}

export function setActionContext(context: ActionContext) {
  setContext(ACTION_CONTEXT_KEY, context);
}

export function getActionContext(): ActionContext | undefined {
  return getContext<ActionContext>(ACTION_CONTEXT_KEY);
}
