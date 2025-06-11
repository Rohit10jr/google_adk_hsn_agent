# Google ADK HSN Validation Agent

## Overview
This project implements an HSN (Harmonized System of Nomenclature) code validation agent using the [Google ADK (Agent Development Kit)](https://github.com/google/adk-python) framework. The agent loads a master HSN code Excel file, provides a tool for validating HSN codes, and includes guardrails for both model and tool calls. It is designed to be run as an ADK agent with a web interface for interactive use.

## 📚 Documentation

For more detailed explanations, diagrams, and examples, see the [`docs/`](./docs) folder:

- [`index.md`](./docs/index.md): Detailed project overview, structure, and design.
- [`index_diagrams.md`](./docs/index_diagrams.md): Architecture diagrams and data flow illustrations.

You can explore these files directly in the repository or view them rendered on GitHub.

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
│   ├── agent.py               # Agent setup and orchestration
│   ├── callback.py            # Guardrails and tool callbacks
│   ├── data_loader.py         # Loads and prepares HSN/SAC data
│   ├── tool.py               # Defines tools for HSN validation
│   └── .env/                  # Environment variables (API keys, configs)
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
git clone https://github.com/Rohit10jr/google_adk_hsn_agent.git
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
- Ensure you have the [Google ADK](https://github.com/google/adk-python) installed and configured.
- You may need to set up credentials or environment variables(.env).

### 2. Start the ADK Web Interface
```powershell
adk web
```
- This will launch the web UI for interacting with your agent.
- By default, the agent is configured in `hsn_agent/agent.py`.

## Modularity & Customization
- **Agent Logic**: Edit `agent.py` to customize the agent’s behavior, tool usage, and overall validation flow.
- **Guardrails**: Modify `callback.py` to update tool guardrails, block rules, or response formatting.
- **Data Handling**: Adjust `data_loader.py` to change how HSN/SAC data is loaded or preprocessed.
- **Tools**: Define or extend tool functionality in `tools.py` — such as HSN code validation or future utilities.
- **Session State**: Currently uses in-memory state via `ToolContext`; replace with persistent storage for production use.


## Troubleshooting
- If you see errors about missing `HSN_SAC.xlsx`, ensure the file exists in `data/` and has the correct columns.
- For dependency issues, check `requirements.txt` and reinstall as needed.
- For ADK-specific issues, refer to the [Google ADK documentation](https://github.com/google/adk-python).

## License
This project is for demonstration and internal use. See the google ADK repository for license details.

---