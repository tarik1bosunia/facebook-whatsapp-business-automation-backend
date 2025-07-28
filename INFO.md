# in every product need to save FAQ
# count number of token, save to db, per business user

I want to get a architechture from you... just give me the graph with description
businessman some products, services. have brand_persona. and some FAQ . here cutomer sent message to the website , agent decite the message sent   to llm(gemini) , then gemini reply to agent , agent give reply to customer or used tool then call llm again , llm reply, .call tool or reply user ... continue, i will use lang graph . just give the visualization with proper description

```plaintext

┌───────────────────────────────────────────────────────────────────────┐
│                            LANGGRAPH WORKFLOW                         │
├───────────────────┬───────────────────┬───────────────────┬───────────┤
│    AGENT ROUTER   │     LLM NODE      │    TOOL NODE      │ RESPONSE  │
│   (Decision Hub)  │    (Gemini)       │  (API Actions)    │ FORMATTER │
├─────────┬─────────┼─────────┬─────────┼─────────┬─────────┼───────────┤
│ Input:  │  FAQ    │ Input:  │ Needs   │ Input:  │ Tool    │ Input:    │
│ Message │ Match?  │ Message │ Tool?   │ Tool    │ Result  │ LLM/FAQ   │
│         │         │ +       │         │ Request │         │ Output    │
│         │         │ Context │         │         │         │           │
├─────────┴────┬────┴────┬────┴────┬────┴────┬────┴────┬────┴────┬──────┤
│              │         │         │         │         │         │      │
│  Yes ────────┘         │ No ─────┘         │         │         │      │
│                        │                   │         │         │      │
│  No                    │ Yes               │         │         │      │
│                        │                   │         │         │      │
│  ▼                     ▼                   ▼         ▼         ▼      │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │                         STATE OBJECT                          │   │
│  ├───────────────────────────────────────────────────────────────┤   │
│  │ {                                                            │   │
│  │   "message": "Order status?",                                │   │
│  │   "needs_tool": True,                                        │   │
│  │   "tool_name": "order_api",                                  │   │
│  │   "tool_args": {"order_id": 123},                            │   │
│  │   "llm_output": null,                                        │   │
│  │   "tool_result": {"status": "shipped"}                       │   │
│  │ }                                                            │   │
│  └───────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────────┘

FLOW EXPLANATION:
1. Customer Message → Agent Router
   ├─ FAQ Match → Response Formatter → Customer
   └─ Needs LLM → LLM Node
       ├─ No Tools → Response Formatter → Customer
       └─ Needs Tool → Tool Node → (Update State) → LLM Node → ...
```
---
```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#ffccff', 'edgeLabelBackground':'#fff'}}}%%
flowchart TD
    A[("fa:fa-user Customer Message")] --> B{{Agent Router}}
    B -->|FAQ Match| C[[Cache Response]]
    B -->|Needs LLM| D[["fa:fa-brain Gemini LLM"]]
    D --> E{Tool Required?}
    E -->|Yes| F[["fa:fa-gear Tool Node"]]
    E -->|No| G[["fa:fa-comment Response Formatter"]]
    F -->|tool_result| D
    G --> H[("fa:fa-user Customer")]
    C --> H
    H -->|New Message| A

    classDef io fill:#ffcc99,stroke:#333,stroke-width:2px
    classDef decision fill:#ffccff,stroke:#333,stroke-width:2px
    classDef llm fill:#99ccff,stroke:#333,stroke-width:2px
    classDef tool fill:#99ff99,stroke:#333,stroke-width:2px
    
    class A,H io
    class B decision
    class D llm
    class F tool

```

