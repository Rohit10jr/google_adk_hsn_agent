import asyncio
from google.genai import types
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from .callback import block_hsn_code_tool_guardrail, block_keyword_model_guardrail
from .tool import hsn_code_validation_tool
from .prompt import description, instruction
from dotenv import load_dotenv
load_dotenv() 

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