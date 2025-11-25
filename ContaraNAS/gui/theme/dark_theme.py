from ContaraNAS.gui.theme.theme import ColorShades, Shadows, Theme, ThemeMode


DARK_THEME = Theme(
    name="Dark",
    mode=ThemeMode.DARK,
    # Backgrounds
    bg_base="#0f0f14",
    bg_surface="#1a1a24",
    bg_elevated="#252532",
    bg_input="#1a1a24",
    # Text
    text_primary="#f1f5f9",
    text_secondary="#94a3b8",
    text_muted="#64748b",
    text_inverse="#0f172a",
    # Borders
    border_default="#2d2d3a",
    border_subtle="#1f1f2a",
    # Primary (Blue)
    primary=ColorShades("#1d4ed8", "#2563eb", "#3b82f6", "#60a5fa", "#93c5fd"),
    # Success
    success=ColorShades("#15803d", "#22c55e", "#4ade80", "#86efac", "#bbf7d0"),
    # Warning
    warning=ColorShades("#ea580c", "#f97316", "#fb923c", "#fdba74", "#fed7aa"),
    # Danger
    danger=ColorShades("#dc2626", "#ef4444", "#f87171", "#fca5a5", "#fecaca"),
    # Info
    info=ColorShades("#0891b2", "#06b6d4", "#22d3ee", "#67e8f9", "#a5f3fc"),
    # Neutral
    neutral=ColorShades("#374151", "#4b5563", "#6b7280", "#9ca3af", "#d1d5db"),
    # Shadows (more subtle for dark mode)
    shadows=Shadows(
        none="none",
        sm="inset 0 1px 0 0 rgba(255,255,255,0.05), 0 1px 3px 0 rgba(0,0,0,0.3)",
        md="inset 0 1px 0 0 rgba(255,255,255,0.08), 0 4px 6px -1px rgba(0,0,0,0.4)",
        lg="inset 0 1px 0 0 rgba(255,255,255,0.1), 0 10px 15px -3px rgba(0,0,0,0.5)",
        inset="inset 0 2px 4px rgba(0,0,0,0.4), inset 0 -1px 0 rgba(255,255,255,0.03)",
    ),
    # Graph colors (brighter)
    graph_primary="#60a5fa",
    graph_secondary="#4ade80",
    graph_tertiary="#fb923c",
    graph_quaternary="#a78bfa",
    graph_fill_opacity=0.25,
)
