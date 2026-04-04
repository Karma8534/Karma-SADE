# Chrome 146 Gemini Nano Integration — Design Context

## What
Chrome 146 (installed on P1, obs #22352) includes built-in Gemini Nano with:
- Prompt API: text generation in-browser, zero API cost
- Summarizer API: condense text locally
- Writer/Rewriter API: generate/edit text locally
- All run in-browser via Chrome's built-in model

## Why
This enables the Nexus frontend (hub.arknexus.net) to:
1. Classify messages locally IN THE BROWSER before sending to any backend
2. Summarize long responses for mobile-friendly display
3. Generate quick responses for simple queries without hitting ANY API
4. Pre-process user input (intent detection, entity extraction) at zero cost

## How It Maps to Nexus
```
CURRENT:
  Browser → proxy.js → K2/Groq/CC

WITH CHROME NANO:
  Browser → Chrome Nano (classify/summarize, 0ms API) → proxy.js → K2/Groq/CC
  Simple queries answered IN THE BROWSER. Never leave the device.
```

## Implementation Path
1. Feature-detect Chrome AI APIs in frontend
2. For simple queries: try Prompt API first
3. For long responses: use Summarizer API for mobile
4. For message classification: use Prompt API to determine routing tier

## Prerequisites
- Chrome 146+ (confirmed on P1)
- origin trial or flags enabled for Prompt API
- Gemini Nano model downloaded (happens automatically)

## Blockers
- API is Chrome-only (not Firefox/Safari)
- Model capabilities are limited (small model)
- May need origin trial enrollment

## Status: DESIGN COMPLETE — needs Chrome API testing in future session
