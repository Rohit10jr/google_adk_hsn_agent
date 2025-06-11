# HSN Validation Agent - ADK Design & Implementation Documentation

## 1. Agent Design
### Architecture Overview
The HSN Validation Agent is built using the Google ADK (Agent Developer Kit) framework. The agent is structured as a Python class (`Agent`) that encapsulates:
- **Intents**: The primary intent is to validate HSN codes provided by the user.
- **Entities**: HSN codes (single or multiple) extracted from user input.
- **Fulfillment Logic**: Implemented as a tool (`hsn_code_validation_tool`) that performs validation against a master dataset.
- **Data Store**: An in-memory dictionary loaded from an Excel file (`HSN_SAC.xlsx`).
- **Callbacks/Guardrails**: Functions to enforce input and tool usage policies.

### Key Components
- **Agent**: The root agent (`root_agent`) is configured with a name, model, description, instructions, tools, and callbacks.
- **Tool**: `hsn_code_validation_tool` validates HSN codes and returns structured results.
- **Callbacks**: 
  - `block_keyword_model_guardrail` (blocks inappropriate user input)
  - `block_hsn_code_tool_guardrail` (blocks restricted HSN codes)
- **Session Service**: Uses `InMemorySessionService` for stateful interactions.

### User Input Handling
- Accepts both single and multiple HSN codes (as a list of strings).
- Input is validated for type and format before processing.

### Output/Response
- Returns a list of results for each input HSN code, including validity, description (if valid), or error reason (if invalid).

---

## 2. Data Handling
### Accessing and Processing the Master Data
- The agent loads the `HSN_SAC.xlsx` file at startup using `pandas.read_excel`.
- Data is stored in a dictionary (`hsn_master_data`) mapping HSN codes to descriptions for fast lookup.
- The file must have columns: `HSNCode` and `Description`.

### Efficiency Considerations
- **Pre-loading**: Data is loaded once at startup and kept in memory, ensuring O(1) lookup for validation.
- **Trade-offs**: Pre-loading is efficient for read-heavy, moderate-size datasets. For very large files, consider chunking or database storage.
- **On-demand loading**: Not used here, as it would slow down each validation and complicate concurrency.

---

## 3. Validation Logic
### Rules Implemented
- **Format Validation**: Checks if each HSN code is a string of digits and has a length of 2, 4, 6, or 8.
- **Existence Validation**: Checks if the code exists in the preloaded dictionary (from the Excel file).

### (Optional) Hierarchical Validation
- For advanced use, the agent could check if parent codes (e.g., for 8-digit code `01011010`, check `010110`, `0101`, `01`) exist in the dataset.
- This adds value by providing context or fallback validation, e.g., if a specific code is missing but a parent exists, the agent can inform the user.

---

## 4. Agent Response
- **Valid HSN Code**: Returns `{input_hsn, is_valid: True, description, message: 'HSN code is valid.'}`
- **Invalid HSN Code**: Returns `{input_hsn, is_valid: False, reason_code, message}`
  - `reason_code` can be `INVALID_FORMAT`, `NOT_FOUND`, `DATASTORE_UNAVAILABLE`, etc.
  - `message` provides a human-readable explanation.

---

## 5. Steps to Build This Agent Using ADK
1. **Set up the project structure** (see README for details).
2. **Implement data loading** from Excel to an in-memory dictionary.
3. **Define validation logic** in a tool function.
4. **Configure the agent** with tools, callbacks, and session management.
5. **Implement guardrails** for both model and tool calls.
6. **Test the agent** with various HSN code inputs.
7. **Run the agent** using `adk web` for a web interface.

---

## Deliverables
- Source code (`hsn_agent/agent.py`)
- Documentation (`docs/index.md`, `readme.md`)
- Run instructions (`readme.md`)

---
