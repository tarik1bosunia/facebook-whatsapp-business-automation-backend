```plaintext

┌───────────────────────────────────────────────────────────────────────────────┐
│                                                                               │
│                            CUSTOMER MESSAGE FLOW                              │
│                                                                               │
└───────────────────┬───────────────────────────────────────────┬───────────────┘
                    │                                           │
                    v                                           v
┌─────────────────────────────────┐                 ┌───────────────────────────┐
│                                 │                 │                           │
│      POSTGRESQL DATABASE        │                 │      AGENT DECISION       │
│                                 │                 │                           │
│ ┌─────────────────────────────┐ │                 │ 1. Analyze message        │
│ │                             │ │                 │ 2. Decide:                │
│ │        Conversation         │ │                 │    - Direct reply?       │
│ │                             │ │                 │    - Need LLM?            │
│ └─────────────────────────────┘ │                 │    - Need tool?           │
│                                 │                 │                           │
│ ┌─────────────────────────────┐ │                 └──────────────┬────────────┘
│ │                             │ │                                │
│ │        ChatMessage          │ │                                │
│ │                             │ │                                v
│ └─────────────────────────────┘ │                 ┌───────────────────────────┐
│                                 │                 │                           │
└─────────────────────────────────┘                 │        TOOL CALL          │
                                                    │                           │
                                                    │ (External APIs/services   │
                                                    │  for specific tasks)      │
                                                    │                           │
                                                    └──────────────┬────────────┘
                                                                   │
                                                                   v
┌───────────────────────────────────────────────────────────────────────────────┐
│                                                                               │
│                              LLM (Gemini) INTERACTION                         │
│                                                                               │
│ ┌─────────────────────────────────────────────────────────────────────────┐  │
│ │                                                                         │  │
│ │  Context:                                                               │  │
│ │  - Current conversation history                                         │  │
│ │  - Brand persona                                                       │  │
│ │  - Products/Services info                                              │  │
│ │  - FAQ knowledge                                                       │  │
│ │                                                                         │  │
│ └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
│                                                                               │
│ 1. Agent sends message + context to Gemini                                   │
│ 2. Gemini generates response or requests tool usage                          │
│ 3. Process continues until final response is ready                           │
│                                                                               │
└───────────────────────────────────┬───────────────────────────────────────────┘
                                    │
                                    v
┌───────────────────────────────────────────────────────────────────────────────┐
│                                                                               │
│                            RESPONSE TO CUSTOMER                               │
│                                                                               │
│ 1. Final response stored in DB                                                │
│ 2. Sent back through original channel                                        │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

```mermaid
stateDiagram-v2
    [*] --> process_input
    process_input --> select_tools: "Processed query"
    select_tools --> execute_tools: "Selected tools"
    execute_tools --> generate_response: "Tool results"
    generate_response --> [*]: "Final response"
    
    state select_tools {
        [*] --> prepare_prompt: "Create tool descriptions"
        prepare_prompt --> llm_decision: "Send to LLM"
        llm_decision --> parse_output: "Get JSON response"
        parse_output --> handle_result: "Validate selection"
        handle_result --> [*]: "Return selected tools"
        
        state handle_result {
            [*] --> success_case: "Valid selection"
            success_case --> [*]
            
            [*] --> error_case: "Selection failed"
            error_case --> fallback: "Use all tools"
            fallback --> [*]
        }
    }
    
    state execute_tools {
        [*] --> route_execution: "Based on selection"
        route_execution --> product_search: "If selected"
        route_execution --> document_search: "If selected"
        product_search --> aggregate
        document_search --> aggregate
        aggregate --> [*]
    }

```

```mermaid
graph LR
    A[process_input] --> B{LLM decides}
    B -->|Needs products| C[ProductSearch]
    B -->|Needs docs| D[DocumentSearch]
    B -->|Both| C & D
    C & D --> E[generate_response]
```

```mermaid
stateDiagram-v2
    [*] --> process_input
    process_input --> select_tools: "user_query"
    select_tools --> execute_tools: "selected_tools"
    execute_tools --> generate_response: "tool_results"
    generate_response --> [*]
    
    state select_tools {
        [*] --> gemini_prompt: "Create numbered tool list"
        gemini_prompt --> get_response: "Send to Gemini"
        get_response --> parse_json: "Extract tool numbers"
        parse_json --> map_tools: "Convert numbers to tools"
        map_tools --> [*]: "Return selected tools"
        
        state error_handling {
            [*] --> parse_error: "If JSON invalid"
            parse_error --> fallback: "Use all tools"
            fallback --> [*]
        }
    }
    
    state execute_tools {
        [*] --> check_selection: "Verify tools"
        check_selection --> run_sequential: "Run selected tools"
        run_sequential --> aggregate: "Collect results"
        aggregate --> [*]
    }
````

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#e3f2fd'}}}%%
graph LR
    A[Customer Message] --> B[Agent Executor]
    B --> C{LLM Tool Selection}
    C -->|"ProductSearch"| D[Execute Product Tool]
    C -->|"No tools"| E{LLM Response Generator}
    D --> E
    E --> F[Final Answer]
    
    style C fill:#fff8e1,stroke:#ffc107
    style E fill:#fff3e0,stroke:#ffa000
    linkStyle 1 stroke:#9e9e9e,stroke-width:2px
```



```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'fontFamily': 'Arial', 'primaryColor': '#E3F2FD', 'edgeLabelBackground':'#ffffff'}}}%%
graph TD
    A([🧑 User Query]) --> B{🤖 LLM Select Tool}

    B -->|📝 Final Answer Tool| E([✅ Stop])
    B -->|🔧 Other Tool| C([🛠 Run Tool])
    
    C --> D([📨 Return Output to LLM])
    D --> B

    %% Node Styles
    style A fill:#E3F2FD,stroke:#1565C0,stroke-width:2px
    style B fill:#FFF8E1,stroke:#FF8F00,stroke-width:2px
    style C fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px
    style D fill:#FFF9C4,stroke:#FBC02D,stroke-width:2px
    style E fill:#C8E6C9,stroke:#388E3C,stroke-width:2px

    %% Link Styles
    linkStyle 0 stroke:#1E88E5,stroke-width:2px
    linkStyle 1 stroke:#43A047,stroke-width:2px
    linkStyle 2 stroke:#FDD835,stroke-width:2px
    linkStyle 3 stroke:#FB8C00,stroke-width:2px

```

#  Why Use KV Caching?
i have to know how to enable caching in gemini and chatgpt model
- Cost saving: Don’t reprocess repeated context.

- Speed: Significantly faster inference.

- Ideal for: Multi-turn chat, long documents, LangGraph loops.