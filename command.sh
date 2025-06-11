echo "Starting HSN Agent using ADK..."

# make the script executable using this command:
# chmod +x command.sh

source venv/Scripts/activate

COMMAND=$1

if [ "$COMMAND" = "run" ]; then
  adk web
elif [ "$COMMAND" = "server" ]; then
  adk api_server
fi
