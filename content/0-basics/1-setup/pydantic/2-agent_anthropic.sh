# install Pydantic AI with Anthropic support
uv add pydantic-ai[anthropic]

# python-dotenv is included — load .env with: from dotenv import load_dotenv; load_dotenv()
# alternative: set your API key directly in the shell
export ANTHROPIC_API_KEY="sk-ant-..."
