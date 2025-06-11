from google.adk.agents import Agent
from typing import List, Dict, Union, Any, Optional
import os
import pandas as pd
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from .callback import block_hsn_code_tool_guardrail, block_keyword_model_guardrail
from .tool import hsn_code_validation_tool
from .prompt import description, instruction


# --- Initialize the Session Memory for Agent ---
APP_NAME = "hsn_code_agent"
SESSION_ID_STATEFUL = "session_state_demo_001"
USER_ID_STATEFUL = "user_state_demo"
session_service_stateful = InMemorySessionService()

session_stateful = session_service_stateful.create_session(
    app_name=APP_NAME, 
    user_id=USER_ID_STATEFUL,
    session_id=SESSION_ID_STATEFUL
)

print(f"Session '{SESSION_ID_STATEFUL}' created for user '{USER_ID_STATEFUL}'.")


# --- Initialize the Root Agent ---
root_agent = Agent(
    name="hsn_code_agent",
    model="gemini-1.5-flash-001",
    description=description,
    instruction=instruction, 
    tools=[hsn_code_validation_tool],
    output_key="hsn_agent_last_response",
    before_model_callback=block_keyword_model_guardrail, 
    before_tool_callback=block_hsn_code_tool_guardrail
)

print("\n--- Agent configuration complete. Ready for 'adk web' command. ---")