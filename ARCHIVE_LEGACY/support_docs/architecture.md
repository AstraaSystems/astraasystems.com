# Ardhanarishvara — System Architecture

## Overview
Ardhanarishvara is a modular, async-driven, IPC-based autonomous engine.

## Core Layers
1. Execution Engine (/execution)
2. Cognitive Agents (/entities)
3. Infrastructure (/infrastructure)
4. Meta-Cognitive Layer (/meta_cognitive)
5. Support Documentation (/support_docs)

## Data Flow
market.data → MathEngine → Arka → Aruhan → IBKRExecution → Ledger

income → Astraa → TreasuryAgent → Ledger

alerts → Disturition → kill.switch → AutonomousSystem shutdown

## IPC Backbone
All modules communicate through GlobalIPC.
