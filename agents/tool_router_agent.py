from pydantic_ai_mock import OpenAIChatModel, PydanticAgent
from pydantic import BaseModel

class ToolRouterOutput(BaseModel):
    tool_name: str  # e.g., search, chat, summarize, ...
    reasoning: str  # explanation for tool selection

class ToolRouterAgent:
    def __init__(self):
        self.model = OpenAIChatModel(
            model="gpt-3.5-turbo",
            api_key_env="OPENROUTER_API_KEY"
        )
        self.agent = PydanticAgent(
            model=self.model,
            system_prompt=(
                "You are a tool router agent. Given a user's query, user context, and chat history, analyze the intent and select the most suitable tool to handle it. "
                "Output a JSON object like this: { \"tool_name\": <tool>, \"reasoning\": \"...\" }\n"
                "Possible tools: search, chat, summarize, recommend, classify.\n"
                "Explain clearly why you chose that tool.\n"
                "You MUST consider user context and chat history if relevant.\n"
                "\n"
                "Examples:\n"
                "Input: {\"query\": \"Tìm tài liệu về chính sách bảo mật.\", \"user_context\": {\"role\": \"admin\"}, \"chat_history\": [\"Tìm tài liệu về bảo mật hệ thống\"]}\n"
                "Output: {\"tool_name\": \"search\", \"reasoning\": \"The user is an admin and has recently searched for security documents, so search is appropriate.\"}\n"
                "Input: {\"query\": \"Giải thích giúp tôi về quy trình đăng ký.\", \"user_context\": {\"role\": \"user\"}, \"chat_history\": []}\n"
                "Output: {\"tool_name\": \"chat\", \"reasoning\": \"The user wants an explanation, so chat is suitable.\"}\n"
            ),
            output_model=ToolRouterOutput
        )

    def analyze(self, query: str, user_context: dict = None, chat_history: list = None) -> ToolRouterOutput:
        input_data = {
            "query": query,
            "user_context": user_context or {},
            "chat_history": chat_history or []
        }
        return self.agent.run(input_data) 