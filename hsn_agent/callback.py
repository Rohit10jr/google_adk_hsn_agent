from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types
from typing import List, Dict, Union, Any, Optional
import random 


# --- Initialize Callback for model and tool ---
def block_keyword_model_guardrail(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    Inspects the latest user message for blocked words. If found, rejects the LLM call
    and returns a predefined LlmResponse. Otherwise, returns None to proceed.
    """
    agent_name = callback_context.agent_name 
    print(f"--- Callback: block_keyword_model_guardrail running for agent: {agent_name} ---")

    # Extract the text from the latest user message in the request history
    last_user_message_text = ""
    if llm_request.contents:
        for content in reversed(llm_request.contents):
            if content.role == 'user' and content.parts:
                if content.parts[0].text:
                    last_user_message_text = content.parts[0].text
                    break

    print(f"--- Callback: Inspecting last user message: '{last_user_message_text[:100]}...' ---") 

    # --- Guardrail Logic ---
    keywords_to_block = ["STUPID", "IDIOT"]

    blocked_responses = [
        "I'm sorry, I cannot process this request as it contains inappropriate language.",
        "This query cannot be processed due to the presence of a blocked word.",
        "To maintain a respectful environment, I am unable to respond to messages containing certain terms.",
        "Your request has been flagged and cannot be completed.",
        "I cannot proceed with this request. Please rephrase your query without using blocked words."
    ]

    for keyword in keywords_to_block:
        if keyword in last_user_message_text.upper():
            print(f"--- Callback: Found '{keyword}'. Blocking LLM call! ---")
            callback_context.state["guardrail_block_keyword_triggered"] = True
            random_message = random.choice(blocked_responses)

            return LlmResponse(
                content=types.Content(
                    role="model",
                    parts=[types.Part(text=random_message)],
                    # parts=[types.Part(text=f"I cannot process this request because it contains a blocked term.")],
                )
            )

    print(f"--- Callback: No blocked keywords found. Allowing LLM call for {agent_name}. ---")
    return None # Returning None signals ADK to continue normally


# callback for tool
def block_hsn_code_tool_guardrail(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    """
    Updated guardrail callback for HSN code validation.
    Filters out blocked HSN codes, modifies args accordingly,
    and returns a detailed result dictionary.
    """
    tool_name = tool.name
    agent_name = tool_context.agent_name
    print(f"--- Callback: Running guardrail for tool '{tool_name}' in agent '{agent_name}' ---")
    print(f"--- Callback: Inspecting args: {args} ---")

    target_tool_name = "hsn_code_validation_tool"
    if tool_name != target_tool_name:
        return None  # Only act on the intended tool

    hsn_codes_to_check = args.get("hsn_inputs", [])
    if not hsn_codes_to_check:
        return None

    unblocked_codes = []
    blocked_codes = []

    for code in hsn_codes_to_check:
        if isinstance(code, str) and code.strip().startswith("12345"):
            blocked_codes.append(code.strip())
        else:
            unblocked_codes.append(code.strip())

    # If all codes are valid, proceed as usual
    if not blocked_codes:
        print(f"--- Callback: All HSN codes valid. Proceeding with original tool call. ---")
        return None

    # Modify args to exclude invalid codes
    args["hsn_inputs"] = unblocked_codes

    # Add a helpful message for the LLM
    tool_context.state["guardrail_hsn_block_triggered"] = True
    tool_context.state["llm_message"] = (
        f"Some HSN codes were blocked due to policy restrictions and have been removed from the tool call.\n\n"
        f" Blocked codes: {blocked_codes}\n"
        f" Unblocked codes: {unblocked_codes}\n"
        f"Please run the tool call using only the unblocked codes to check if they exist in the master data and return their corresponding descriptions to user."
)

    print(f"--- Callback: Returning structured block response with valid and invalid codes. ---")

    return {
        "unblocked_codes": unblocked_codes,
        "blocked_codes": blocked_codes,
        "llm_message": tool_context.state["llm_message"],
        "next_action": "RETRY_WITH_FILTERED_INPUT"
    }


