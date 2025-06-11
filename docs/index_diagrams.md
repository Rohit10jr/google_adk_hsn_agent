# HSN Validation Agent - Diagrams & Examples

## 1. Architecture Diagram

```mermaid
graph TD
    A[User] -->|Input HSN Codes| B[ADK Web UI]
    B --> C[HSN Validation Agent]
    C --> D{Guardrails}
    D -->|Model Guardrail| E[Block inappropriate input]
    D -->|Tool Guardrail| F[Block restricted HSN codes]
    C --> G[HSN Validation Tool]
    G --> H[HSN Master Data (Excel/In-Memory)]
    G --> I[Validation Results]
    I --> B
    B --> A
```

---

## 2. Data Flow Example

1. **User Input:**
   - User enters: `["12345678", "0101", "99999999"]`
2. **Agent Processing:**
   - Model guardrail checks for inappropriate language (passes).
   - Tool guardrail checks for restricted codes (e.g., codes starting with `12345` are blocked).
   - Valid codes are passed to the validation tool.
3. **Validation Tool:**
   - Checks format (numeric, length 2/4/6/8).
   - Looks up each code in the in-memory HSN master data.
4. **Output:**
   - For each code, returns validity, description (if valid), or error reason.

---

## 3. Example Agent Responses

### Example 1: All Valid Codes
**Input:** `["0101", "1002"]`

**Output:**
```json
[
  {"input_hsn": "0101", "is_valid": true, "description": "Live animals", "message": "HSN code is valid."},
  {"input_hsn": "1002", "is_valid": true, "description": "Wheat and meslin", "message": "HSN code is valid."}
]
```

### Example 2: Invalid and Blocked Codes
**Input:** `["12345678", "99999999", "abcd"]`

**Output:**
```json
[
  {"input_hsn": "12345678", "is_valid": false, "reason_code": "BLOCKED_BY_GUARDRAIL", "message": "HSN code blocked by policy."},
  {"input_hsn": "99999999", "is_valid": false, "reason_code": "NOT_FOUND", "message": "HSN code not found in master data."},
  {"input_hsn": "abcd", "is_valid": false, "reason_code": "INVALID_FORMAT", "message": "HSN code must be numeric and 2, 4, 6, or 8 digits long."}
]
```

---

## 4. (Optional) Hierarchical Validation Example
**Input:** `"01011010"`

**Output:**
```json
{
  "input_hsn": "01011010",
  "is_valid": false,
  "reason_code": "NOT_FOUND",
  "message": "HSN code not found. However, parent codes found: ['010110', '0101', '01']"
}
```

---

*Diagrams and examples for interview and documentation purposes. Last updated: 2025-06-11.*
