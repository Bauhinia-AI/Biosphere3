from langchain_openai import ChatOpenAI
from collections import defaultdict
from typing import Dict, DefaultDict
from dotenv import load_dotenv
import os
from langchain.callbacks.base import BaseCallbackHandler

load_dotenv()


class LLMSelector:
    token_usage: DefaultDict[str, Dict[str, int]] = defaultdict(
        lambda: {"prompt": 0, "completion": 0, "total": 0}
    )

    @classmethod
    def get_token_usage(cls) -> Dict[str, Dict[str, int]]:
        return dict(cls.token_usage)

    @classmethod
    def _update_token_usage(cls, model_name: str, usage_data: dict):
        if "token_usage" in usage_data:
            token_data = usage_data["token_usage"]
            cls.token_usage[model_name]["prompt"] += token_data.get("prompt_tokens", 0)
            cls.token_usage[model_name]["completion"] += token_data.get(
                "completion_tokens", 0
            )
            cls.token_usage[model_name]["total"] += token_data.get("total_tokens", 0)

    @classmethod
    def get_llm(cls, model_name: str, temperature: float = 0.7):
        # supported models: gpt-4o, gpt-4o-mini, deepseek
        callbacks = [TokenUsageHandler(model_name)]

        if model_name.startswith("gpt"):
            return ChatOpenAI(
                base_url="https://api.aiproxy.io/v1",
                api_key=os.getenv("OPENAI_API_KEY"),
                model=model_name,
                temperature=temperature,
                callbacks=callbacks,
            )
        elif model_name.startswith("deepseek"):
            return ChatOpenAI(
                base_url="https://api.deepseek.com/v1",
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                model=model_name,
                temperature=temperature,
                callbacks=callbacks,
            )
        else:
            raise ValueError(f"Unsupported model: {model_name}")


class TokenUsageHandler(BaseCallbackHandler):
    def __init__(self, model_name: str):
        self.model_name = model_name
        super().__init__()

    def on_llm_end(self, response, **kwargs):
        if hasattr(response, "llm_output") and response.llm_output:
            token_usage = response.llm_output.get("token_usage", {})
            usage_data = {"token_usage": token_usage}
            LLMSelector._update_token_usage(self.model_name, usage_data)
