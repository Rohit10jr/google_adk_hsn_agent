from google.adk.tools.tool_context import ToolContext
from typing import List, Dict, Union, Any, Optional
from .data_loader import hsn_master_data

# --- Part 3: Initialize the tool for agent ---
def hsn_code_validation_tool(hsn_inputs: List[str], tool_context:ToolContext) -> List[Dict[str, Any]]:
    """
    Validates one or more HSN codes against the pre-loaded HSN master data.
    This tool should be used for all HSN validation requests. It takes either a 
    single HSN code as a string or a list of HSN codes as strings.
    """
    print(f"--- Tool 'hsn_code_validation_tool' called with: {hsn_inputs} ---")

    # Check if the data store was loaded successfully
    if not hsn_master_data:
        return [{
            "input_hsn": str(hsn_inputs),
            "is_valid": False,
            "reason_code": "DATASTORE_UNAVAILABLE",
            "message": "The HSN master data failed to load at startup. Cannot perform validation."
        }]

    if not isinstance(hsn_inputs, list):
        return [{
            "input_hsn": str(hsn_inputs),
            "is_valid": False,
            "reason_code": "INVALID_INPUT_TYPE",
            "message": "Input must be a list of strings."
        }]

    results = []
    for code in hsn_inputs:
        # Perform all validation checks as before
        if not isinstance(code, str):
            results.append({"input_hsn": str(code), "is_valid": False, "reason_code": "INVALID_ITEM_TYPE", "message": "Each HSN code must be a string."})
            continue

        clean_code = code.strip()

        if not clean_code.isdigit() or len(clean_code) not in {2, 4, 6, 8}:
            results.append({"input_hsn": code, "is_valid": False, "reason_code": "INVALID_FORMAT", "message": "HSN code must be numeric and 2, 4, 6, or 8 digits long."})
            continue

        # This is now an extremely fast lookup in the in-memory dictionary
        description = hsn_master_data.get(clean_code)

        if description:
            results.append({"input_hsn": code, "is_valid": True, "description": description, "message": "HSN code is valid."})
        else:
            # --- Hierarchical Validation Logic ---
            parent_found = False
            # Check for parents of an 8-digit or 6-digit code
            if len(clean_code) in [6, 8]:
                parent_code = clean_code[:-2]  # Check for 6-digit or 4-digit parent
                parent_description = hsn_master_data.get(parent_code)
                if parent_description:
                    results.append({
                        "input_hsn": code,
                        "is_valid": False,
                        "reason_code": "NOT_FOUND_BUT_PARENT_EXISTS",
                        "message": f"Code not found, but its parent category '{parent_code}' ({parent_description}) is valid."
                    })
                    parent_found = True
            # Check for the 2-digit chapter of a 4-digit code if no other parent was found
            if not parent_found and len(clean_code) >= 4:
                parent_code = clean_code[:2]  # Check for 2-digit chapter
                parent_description = hsn_master_data.get(parent_code)
                if parent_description:
                    results.append({
                        "input_hsn": code,
                        "is_valid": False,
                        "reason_code": "NOT_FOUND_BUT_PARENT_EXISTS",
                        "message": f"Code not found, but its parent chapter '{parent_code}' ({parent_description}) is valid."
                    })
                    parent_found = True

            if not parent_found:
                results.append({
                    "input_hsn": code,
                    "is_valid": False,
                    "reason_code": "NOT_FOUND",
                    "message": "HSN code not found in master data, and no valid parent category was found."
                })

    tool_context.state["hsn_tool_last_result"] = results

    return results