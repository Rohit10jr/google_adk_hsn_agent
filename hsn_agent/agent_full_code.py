import asyncio
from google.genai import types
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from typing import List, Dict, Union, Any, Optional
import os
import pandas as pd
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types
import random 
from dotenv import load_dotenv
load_dotenv()

# --- Agent descriptions and instructions --- 
description="Agent to validate and look up HSN codes using a preloaded master data file."

instruction="""
    You are a helpful and efficient assistant for validating HSN codes. 
    Your primary goal is to understand the user's request, identify any HSN codes mentioned,
    and use the provided 'hsn_code_validation_tool' to check their validity.
    Present the results from the tool to the user in a clear, easy-to-read format.
    If a code is valid, state its description. If invalid, state the reason.
    Be friendly and conversational in your responses. Use emojis where appropriate to make the interaction engaging (e.g., ✅ for valid, ❌ for invalid, ℹ️ for info).
    After providing results, ask the user if they are satisfied or if they would like to validate more codes (e.g., "Would you like to check another HSN code? 😊").
    If the user seems confused or needs help, offer guidance or examples.
    Confirm if the user is happy with the answer or needs further assistance.
    Thank the user for using the service and encourage feedback for improvement.
    """


# --- load the hsn data file  ---
def load_hsn_data(file_path: str) -> Dict[str, str]:
    """
    Loads HSN data from an Excel file into an efficient in-memory dictionary.
    This function is called once when the application starts.
    """
    if not os.path.exists(file_path):
        print(f"--- CRITICAL ERROR: HSN master file not found at '{file_path}'. The validation tool will be non-functional. ---")
        return {}

    try:
        df = pd.read_excel(file_path, dtype={'HSNCode': str})

        if 'HSNCode' not in df.columns or 'Description' not in df.columns:
            print("--- CRITICAL ERROR: Excel file must contain 'HSNCode' and 'Description' columns. ---")
            return {}

        df.dropna(subset=['HSNCode'], inplace=True)
        df['HSNCode'] = df['HSNCode'].str.strip()
        hsn_map = pd.Series(df.Description.values, index=df.HSNCode).to_dict()
        
        print(f"--- Successfully loaded {len(hsn_map)} HSN codes into memory. ---")
        return hsn_map

    except Exception as e:
        print(f"--- CRITICAL ERROR: An error occurred while reading the Excel file: {e} ---")
        return {}
    
# Load the data into a global variable as our in-memory data store.
script_dir = os.path.dirname(__file__) 
file_path = os.path.join(script_dir, "..", "data", "HSN_SAC.xlsx")
file_path = os.path.abspath(file_path)
hsn_master_data = load_hsn_data(file_path)


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
            f"Please run the tool call using only the unblocked codes to check if they are valid and exist in the master data"
    )
    
    return {
        "unblocked_codes": unblocked_codes,
        "blocked_codes": blocked_codes,
        "llm_message": tool_context.state["llm_message"],
        "next_action": "RETRY_WITH_FILTERED_INPUT"
    }


# --- Initialize the tool for agent ---
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
                        "message": f"HSN Code not found, but its parent category '{parent_code}' ({parent_description}) is valid."
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
                        "message": f"HSN Code not found, but its parent chapter '{parent_code}' ({parent_description}) is valid."
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
    print("--- Agent Tool Result ---")
    print(results)

    return results

# --- Initialize the Session Memory for Agent ---
session_service_stateful = InMemorySessionService()

APP_NAME = "hsn_code_agent"
SESSION_ID_STATEFUL = "session_state_demo_001"
USER_ID_STATEFUL = "user_state_demo"

print(f"Session '{SESSION_ID_STATEFUL}' created for user '{USER_ID_STATEFUL}'.")

# --- Initialize the Root Agent ---
root_agent = Agent(
    name="hsn_code_agent",
    # model="gemini-1.5-flash-001",
    model="gemini-2.0-flash",
    description=description,
    instruction=instruction, 
    tools=[hsn_code_validation_tool],
    output_key="hsn_agent_last_response",
    before_model_callback=block_keyword_model_guardrail, 
    before_tool_callback=block_hsn_code_tool_guardrail
)
print("\n--- Agent configuration complete. Ready for 'adk web' command. ---")

# --- Initialize Runner ---
runner = Runner(
    agent=root_agent, # The agent we want to run
    app_name=APP_NAME,   # Associates runs with our app
    session_service=session_service_stateful # Uses our session manager
)
print(f"Runner created for agent '{runner.agent.name}'.")


async def call_agent_async(query: str, runner: Runner, user_id: str, session_id: str):
    """Sends a query to the agent and prints the final response."""
    
    print(f"\n>>> Calling Agent: '{APP_NAME}' | User Query: {query}")
    user_content = types.Content(role='user', parts=[types.Part(text=query)])
    final_response_text = "Agent did not produce a final response."

    # We iterate through events to find the final answer.
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content):
        # You can uncomment the line below to see *all* events during execution
        #   print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate: # Handle potential errors/escalations
                final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
            break

    print(f"<<< Agent Response: {final_response_text}")
    current_session = await session_service_stateful.get_session(app_name=APP_NAME,
                                                  user_id=user_id,
                                                  session_id=session_id)
    stored_output = current_session.state.get(root_agent.output_key)

    # Pretty print if the stored output looks like JSON (likely from output_schema)
    print(f"--- Session State ['{root_agent.output_key}']: ", end="")


# We need an async function to await our interaction helper
async def run_conversation():
    # Create the specific session where the conversation will happen
    print("--- Testing Agent with Tool ---")
    agent_session = await session_service_stateful.create_session(
        app_name=APP_NAME,
        user_id=USER_ID_STATEFUL,
        session_id=SESSION_ID_STATEFUL
    )
    print(f"Session created: App='{APP_NAME}', User='{USER_ID_STATEFUL}', Session='{SESSION_ID_STATEFUL}'")

    await call_agent_async("find and validate the hsn code 846591",
                                       runner=runner,
                                       user_id=USER_ID_STATEFUL,
                                       session_id=SESSION_ID_STATEFUL)

    await call_agent_async("validate the hsn code 12345",
                                       runner=runner,
                                       user_id=USER_ID_STATEFUL,
                                       session_id=SESSION_ID_STATEFUL)

if __name__ == "__main__":
    try:
        asyncio.run(run_conversation())
    except Exception as e:
        print(f"An error occurred: {e}")