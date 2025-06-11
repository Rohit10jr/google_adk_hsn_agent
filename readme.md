# Google ADK HSN Validation Agent

## Overview
This project implements an HSN (Harmonized System of Nomenclature) code validation agent using the [Google ADK (Agent Development Kit)](https://github.com/google/adk-python) framework. The agent loads a master HSN code Excel file, provides a tool for validating HSN codes, and includes guardrails for both model and tool calls. It is designed to be run as an ADK agent with a web interface for interactive use.

## Features
- **HSN Code Validation Tool**: Validates HSN codes against a preloaded master data file (`HSN_SAC.xlsx`).
- **Guardrails**: Blocks inappropriate user input and restricted HSN codes.
- **Session Management**: Uses in-memory session service for stateful interactions.
- **Web Interface**: Easily launchable via the `adk web` command.

## File Structure
```
.
├── data/
│   └── HSN_SAC.xlsx           # Master Excel file with HSN codes and descriptions
├── docs/
│   └── index.md               # Documentation placeholder
├── hsn_agent/
│   ├── __init__.py            # Package initializer
│   ├── agent.py               # Main agent logic, tool, and callbacks
│   └── __pycache__/           # Python bytecode cache
├── requirements.txt           # Main Python dependencies requirements list
├── .gitignore                 # Git ignore rules
├── readme.md                  # This file
└── venv/                      # virtual environment
```

## HSN Agent Logic
- Loads HSN data from `data/HSN_SAC.xlsx` into memory for fast lookup.
- Provides a tool (`hsn_code_validation_tool`) to validate HSN codes (numeric, 2/4/6/8 digits, must exist in master data).
- Model guardrail blocks user messages with inappropriate language.
- Tool guardrail blocks restricted HSN codes.

## Setup & Installation

### 1. Clone the Repository
```powershell
git clone <your-repo-url>
cd google_adk_hsn_agent
```

### 2. Create and Activate a Virtual Environment (Recommended)
```powershell
python -m venv venv
.\venv\Scripts\Activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Prepare the HSN Master Data
- Place your `HSN_SAC.xlsx` file in the `data/` directory.
- The Excel file must have columns: `HSNCode` and `Description`.

## Running the Agent (ADK Web)

### 1. Set Up Google ADK
- Ensure you have the [Google ADK](https://github.com/google/adk) installed and configured.
- You may need to set up credentials or environment variables(.env).

### 2. Start the ADK Web Interface
```powershell
adk web
```
- This will launch the web UI for interacting with your agent.
- By default, the agent is configured in `hsn_agent/agent.py`.

## Customization
- **Agent Logic**: Modify `hsn_agent/agent.py` to change validation logic, guardrails, or agent instructions.
- **Tool Guardrails**: See `tool_callback.py` for examples and tests of tool guardrail logic.
- **Session State**: The agent uses in-memory session state; adapt as needed for production.

## Troubleshooting
- If you see errors about missing `HSN_SAC.xlsx`, ensure the file exists in `data/` and has the correct columns.
- For dependency issues, check `requirements.txt` and reinstall as needed.
- For ADK-specific issues, refer to the [Google ADK documentation](https://github.com/google/adk-python).

## License
This project is for demonstration and internal use. See the repository or ADK for license details.

---