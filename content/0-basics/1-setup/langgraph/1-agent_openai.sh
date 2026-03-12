# install langchain + langgraph + the OpenAI chat model
uv add langchain langgraph langchain-openai

# no built-in .env loading — use python-dotenv or set directly
export OPENAI_API_KEY="sk-..."
