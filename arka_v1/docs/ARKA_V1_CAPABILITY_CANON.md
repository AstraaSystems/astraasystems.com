# Arka V1 Capability Canon

## Purpose
This document records the confirmed Arka V1 capability map after canon stabilization.

Arka V1 is the local CEO/command console for the Astraa / Arka / Aruhan / Ardhanarishvara ecosystem.

## Confirmed Working Capabilities

### Health / Runtime
- Local server responds at `/health`
- Mode: local
- Name: Arka V1
- Version: 1.0

### Memory
- Active memory supports saving and recalling important facts
- Family memory verified:
  - Wife: Thrilochana
  - First-born son: Bhirav Aditya
- Business memory verified:
  - astraasystems.com is the online source of income and business-critical

### Context Brain
- Structured context blocks can be saved
- Context can be recalled with `show context brain`
- Context is intended to influence future responses and calculations

### Conversation Journal
- Recent interaction logging exists
- Journal recall has been cleaned to avoid dumping noisy Arka responses

### Math OS
- Local Math OS exists in `arka_math_os.py`
- Handles:
  - direct arithmetic
  - yearly/monthly/weekly/daily goals
  - gig/delivery scenarios
  - customer-count revenue targets
  - margin/profit/markup
  - compound growth
  - loan/payment estimates

### Web Source Mode
- Arka does not fabricate live web results
- If live snippets cannot be pulled, Arka returns source/search links
- Flight-price behavior is guarded:
  - no fake fares
  - no ticket holds
  - route/source links only if exact fares cannot be verified

### Astraa Website Health
- Arka can run website health/audit style checks
- Website is treated as business-critical because it is Astraa’s online revenue source

### Product CEO / COO Router
- Arka recognizes Astraa product directives
- Creates product work queue for:
  - Commerce
  - Data
  - Inference
  - Distribution
  - Vault
- Creates competitive pricing queue

### Revenue AI / Growth AI
- Astraa Growth AI concept exists as a website revenue / lead-generation agent
- Purpose:
  - qualify visitors
  - recommend Astraa packages/tools
  - capture leads
  - support revenue conversion
- Status:
  - concept/task/plan layer present
  - deeper implementation belongs in future Brain Kernel / Astraa revenue workflow

### Universal Work Queue
- Unknown action requests can be captured as work items
- This prevents dead fallback behavior

### Approval Guard
- Arka HQ has approval-only autonomy guard
- External/risky actions require explicit authority

### Bridge Layer
- Astraa ↔ Arka bridge evidence exists
- Bridge layer is part of the canon chain:
  Arka → OS → Engines → Astraa → Website → Customer → Revenue

### Remote / Travel Start
- `start_arka_v1.ps1` exists for local startup
- Remote use is intended through Windows/Remote Desktop access to local Arka host

## Known Limitations

### Context Brain
Functional but still early. It stores and recalls context, but deeper reasoning should move into Arka V2 Brain Kernel.

### Web Source Mode
Honest fallback works, but live extraction is not equivalent to full Bing/Copilot web search unless a proper search provider/API or browser connector is added.

### Revenue AI
Concept and queue exist. Full production implementation still requires website integration, lead capture workflow, consent/source logging, and Astraa sales reporting.

### Patch/Repair Files
Arka V1 contains patch/repair/hotfix history from rapid stabilization. These should be archived or reorganized later after V1 is frozen.

## Operating Rule
Do not keep adding scenario-specific patches to Arka V1.

Future intelligence should move into:
- Arka V2 Brain Kernel
- Skill registry
- Memory engine
- Context engine
- Planner
- Executor
- Validator
