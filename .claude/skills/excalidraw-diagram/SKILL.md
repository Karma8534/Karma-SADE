---
name: excalidraw-diagram
description: "Generate production-quality Excalidraw architecture diagrams from natural language. Use when documenting system architecture, data flows, API pipelines, or any design decision that benefits from visual communication. Output is self-validated via Playwright render + layout review. Invoke with /excalidraw-diagram or when asked to draw/diagram/visualize any architecture."
user-invocable: true
---

# Excalidraw Diagram Generator

## Design Philosophy

**Diagrams that argue, not display.** Every shape and grouping must mirror the concept it represents:
- Fan-out structures for one-to-many relationships
- Timeline / left-to-right layouts for sequential flows
- Convergence shapes for aggregation
- Nested boxes for containment / ownership
- Never default to uniform card grids — map visual structure to conceptual structure

**Evidence artifacts.** Technical diagrams include actual code snippets, real endpoint paths, and real JSON payloads inline — not placeholder text.

**Visual self-validation.** After generating the Excalidraw JSON, render it to PNG via Playwright, review for layout issues (overlapping text, misaligned arrows, unbalanced spacing), and fix before presenting.

---

## Workflow

### Step 1: Understand the conceptual structure

Before writing any JSON, answer:
- What is the primary flow direction? (top-down, left-right, radial)
- What are the ownership/containment boundaries?
- What are the one-to-many relationships?
- What data or code evidence should appear inline?

### Step 2: Generate Excalidraw JSON

Output valid Excalidraw JSON (`{"type":"excalidraw","version":2,"elements":[...]}`).

**Element types and when to use:**
- `rectangle` — services, components, containers
- `ellipse` — actors, users, external entities
- `arrow` — directional data flow, API calls
- `line` — bidirectional or structural connections
- `text` — labels, annotations, inline code snippets
- `frame` — group related elements into named layers

**Color system (Karma project palette):**
- P1 components: `#4A90D9` (blue)
- K2 components: `#7B68EE` (purple)
- vault-neo components: `#2ECC71` (green)
- External / third-party: `#95A5A6` (gray)
- Warning / broken: `#E74C3C` (red)
- Approved / working: `#27AE60` (dark green)
- Background fills: use `fillStyle: "hachure"` for containers, `"solid"` for key actors

### Step 3: Write the .excalidraw file

Save to `docs/diagrams/<name>.excalidraw`.

### Step 4: Render and self-validate via Playwright

```javascript
// Use mcp__plugin_playwright_playwright__browser_navigate to open Excalidraw
// Load the JSON via the import API
// Take screenshot with browser_take_screenshot
// Review screenshot for:
//   - Text overflow / truncation
//   - Arrow endpoints not touching their targets
//   - Unbalanced whitespace
//   - Color coding consistent with palette
// Fix and re-render until clean
```

### Step 5: Export PNG

Save final render to `docs/diagrams/<name>.png`.

---

## Example Invocations

```
/excalidraw-diagram Draw the Karma2 system topology: P1=CC+Channels, K2=Karma/Vesper/Aria/KCC, vault-neo=hub-bridge+FalkorDB+FAISS. Show data flows between them.

/excalidraw-diagram Visualize the Vesper watchdog→eval→governor pipeline with the B4+B5 broken bridge highlighted.

/excalidraw-diagram Draw a sequence diagram for the coordination bus: Karma posts message → CC reads via Channels → CC responds → Karma receives.

/excalidraw-diagram Architecture diagram for hub.arknexus.net showing all containers and their roles.
```

---

## Karma-Specific Topology Reference

Use these canonical names and colors in all diagrams:

| Node | Color | Role |
|------|-------|------|
| P1 (Windows, 64GB) | `#4A90D9` | CC server, Channels bridge, KCC |
| K2 (WSL, 8GB GPU) | `#7B68EE` | Karma/Vesper/Aria/KCC |
| vault-neo (DigitalOcean) | `#2ECC71` | hub-bridge, FalkorDB, FAISS, ledger |
| Coordination bus | `#F39C12` | Orange — message routing layer |
| Sovereign (Colby) | `#ECF0F1` | White with dark border — top of hierarchy |

---

## Quality Gate

Before presenting a diagram:
- [ ] Every arrow has a label describing what flows
- [ ] Color coding matches the palette above
- [ ] No overlapping text (verified via Playwright screenshot)
- [ ] The diagram makes an argument (not just a list of boxes)
- [ ] Inline code/endpoint paths are actual values, not placeholders
- [ ] File saved to `docs/diagrams/`
