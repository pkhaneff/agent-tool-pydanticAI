import os
import re
import json
import requests
from dotenv import load_dotenv
from typing import TypeVar, Generic, Type
from pydantic import BaseModel
from datetime import datetime

load_dotenv()

T = TypeVar("T", bound=BaseModel)


class OpenAIChatModel:
    def __init__(self, model: str, api_key_env: str):
        self.model = model
        self.api_key = os.getenv(api_key_env)
        if not self.api_key:
            raise ValueError(f"API key not found. Please set '{api_key_env}' in your .env file.")

    def chat(self, messages):
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://www.facebook.com",
            "Content-Type": "application/json",
            "X-Title": "Draconic Case Study"
        }
        body = {
            "model": self.model,
            "messages": messages
        }

        try:
            response = requests.post(url, headers=headers, json=body, timeout=30)

            # Kiểm tra mã trạng thái HTTP
            response.raise_for_status()

            result = response.json()

            # Kiểm tra format kết quả có đúng không
            if "choices" in result and result["choices"]:
                return result["choices"][0]["message"]["content"]
            else:
                raise ValueError("Invalid response format from OpenRouter API.")

        except requests.exceptions.HTTPError as http_err:
            print("❌ HTTP error:", response.status_code, response.text)
            raise Exception(f"HTTP error occurred: {http_err}")
        except requests.exceptions.RequestException as req_err:
            print("❌ Request failed:", str(req_err))
            raise Exception(f"Request failed: {req_err}")
        except ValueError as val_err:
            print("❌ Invalid response content:", str(val_err))
            raise Exception(f"Invalid response content: {val_err}")
        except Exception as e:
            print("❌ Unexpected error:", str(e))
            raise Exception(f"Unexpected error: {e}")

class PydanticAgent(Generic[T]):
    def __init__(self, model: OpenAIChatModel, system_prompt: str, output_model: Type[T]):
        self.model = model
        self.system_prompt = system_prompt
        self.output_model = output_model
        self.agent_name = output_model.__name__.replace("Output", "") 

    def run(self, input_data: dict, routing_decision: str = "N/A") -> T:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": str(input_data)}
        ]

        output_text = self.model.chat(messages)

        try:
            # Extract first valid JSON object from output
            json_match = re.search(r"{.*?}", output_text, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON object found in model output.")

            json_text = json_match.group(0)
            parsed = json.loads(json_text)

            validated = self.output_model.model_validate(parsed)

            # Write to ai_chat_history.txt
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open("ai_chat_history.txt", "a", encoding="utf-8") as f:
                f.write(f"\n\n [{self.agent_name}Agent] - {timestamp}\n")
                f.write("User Input:\n")
                f.write(str(input_data) + "\n\n")
                f.write("Model Output:\n")
                f.write(json.dumps(parsed, indent=2) + "\n\n")

                if "reasoning" in parsed:
                    f.write("Reasoning:\n")
                    f.write(parsed["reasoning"] + "\n\n")

                f.write(f"Routing Decision: {routing_decision}\n")
                f.write("-" * 50 + "\n")

            return validated

        except Exception as e:
            print("\n Failed to parse output:\n", output_text)
            raise e
