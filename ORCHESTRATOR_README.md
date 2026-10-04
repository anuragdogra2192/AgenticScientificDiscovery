# Master Orchestration Loop: The Scientific Discovery Engine

**Status**: ✅ **FULLY OPERATIONAL**

The **Master Orchestrator** connects all 6 specialist agents into a seamless, intelligent Mycobacterium tuberculosis drug discovery pipeline. Uses Claude Haiku 4.5 for all agents with graceful fallback to rule-based logic. Includes feedback loops, human approval checkpoints, and knowledge graph generation. Complete workflow takes 15-25 seconds with Claude integration.

## 🎼 The Orchestration Symphony (Mtb Omnigent Pipeline)

                    RESEARCH QUESTION
                            ↓
        ┌───────────────────────────────────────┐
        │   📚 PHASE 1: LITERATURE DISCOVERY   │
        │   Europe PMC & OpenAlex search        │
        └───────────────────────┬───────────────┘
                                ↓
        ┌───────────────────────────────────────┐
        │   💡 PHASE 2: HYPOTHESIS GENERATION  │
        │   Claude Haiku gap/hypothesis scoring │
        └───────────────────────┬───────────────┘
                                ↓
        ┌───────────────────────────────────────┐
        │   🧪 PHASE 3: EXPERIMENT PLANNING    │
        │   Comparative BSL-3 protocol & budget │
        └───────────────────────┬───────────────┘
                                ↓
                    ┌──────────────────────┐
                    │ 👤 HUMAN APPROVAL    │
                    │ BSL-3 Safety Gate    │
                    └────────┬─────────────┘
                   Approved ↙    ↘ Rejected
                      ↙            ↘
                    ↙ YES       NO  ↘ STOP
                   ↙
        ┌───────────────────────────────────────┐
        │   ⚙ PHASE 4: EXPERIMENT RUNNER      │
        │   Matched Zheng & Av-Gay controls     │
        └───────────────────────┬───────────────┘
                                ↓
        ┌───────────────────────────────────────┐
        │   📊 PHASE 4b: ANALYSIS AGENT        │
        │   Selectivity Index & Statistics      │
        └───────────────────────┬───────────────┘
                                ↓
                    ┌──────────────────────┐
                    │ Hypothesis Confirmed?│
                    │ (Check Feedback Trigger)│
                    └────────┬─────────────┘
                   YES ↙           ↘ NO (Surprising Results)
                      ↙               ↘
        ┌───────────────────────┐       │
        │ 📝 PHASE 5: REPORT    │       │
        │ APA Paper Synthesis   │       │
        └───────────┬───────────┘       │
                    ↓                   │
        ┌───────────────────────┐       │
        │ 🌐 PHASE 6: KG AGENT  │       │
        │ Update Entity Network │       │
        └───────────┬───────────┘       │
                    ↓                   │
        ┌───────────────────────┐       │
        │ 🔄 PHASE 7: ITERATIVE │       │
        │ Dynamic Next Decision │       │
        └───────────┬───────────┘       │
                    │                   │
                    │           [Refine Query & Loop Back]
                    │                   ↑
                    └───────────────────┘
                                ↓
                  ✅ WORKFLOW COMPLETED (>200× FASTER)
