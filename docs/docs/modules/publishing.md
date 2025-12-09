# Publishing Modules

Guidelines for developing and publishing community modules.

!!! info "Marketplace Coming Soon"
    There is no marketplace yet. This section will be updated when it launches.

---

## Development Guidelines

### Code Quality

- Use type hints throughout your code
- Handle errors gracefully—set `state.error` instead of crashing
- Clean up all resources in `stop_monitoring()`
- Follow PEP 8 style guidelines

### State Management

- Keep state minimal—only store what's needed for the UI
- Call `commit()` after meaningful state changes
- Don't commit in tight loops—batch updates when possible

### UI Design

- Keep tiles concise—show key metrics, not everything
- Use modals for detailed views and forms
- Follow existing module patterns for consistency

### Dependencies

- Minimize dependencies when possible
- Specify minimum versions, not exact versions
- Test on all platforms you claim to support

---

## See Also

- [Module Development Overview](index.md)
- [Module Lifecycle](lifecycle.md)
- [module.json Reference](module-json.md)
