# install langchain + langgraph + the Anthropic chat model
uv add langchain langgraph langchain-anthropic

# no built-in .env loading — use python-dotenv or set directly
export ANTHROPIC_API_KEY="sk-ant-..."
