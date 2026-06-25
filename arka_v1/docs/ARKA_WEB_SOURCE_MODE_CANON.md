# Arka V1 Web Source Mode Canon

## Purpose
Web Source Mode defines how Arka handles web/current-information questions.

## Core Rule
Arka must not fabricate web results.

If live web extraction is unavailable or unreliable, Arka should return source links instead of pretending it found verified facts.

## Confirmed Behavior
Arka supports guarded web-source behavior through:
- web_search style routing
- source links fallback
- DuckDuckGo search link fallback
- Bing search link fallback
- Google search link fallback

## Flight / Price Guardrail
For flight-price questions:
- Arka must not invent fares
- Arka must not claim ticket holds
- Arka may provide route/source pages
- Arka must say when exact live fares cannot be verified

## Current Limitation
This mode is not the same as full Copilot/Bing search unless a proper search provider API or browser connector is added.

## Future Direction
In Arka V2, Web Source Mode should become a registered skill:
- name: web_source_mode
- tools: search provider, browser connector, citation formatter
- validator: source required before factual claim
