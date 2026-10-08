import os
from typing import Any

from langchain.chat_models import init_chat_model
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult


class DryRunModel(BaseChatModel):
    @property
    def _llm_type(self) -> str:
        return "dry-run"

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> ChatResult:
        prompt = "\n".join(str(message.content) for message in messages)
        _, found, answer = prompt.rpartition("\nAnswer: ")
        if not found:
            raise ValueError("the dry-run model needs an 'Answer: ' line in the prompt")
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=answer.strip()))])


def build_model() -> BaseChatModel:
    configured = os.environ.get("MARLOW_MODEL", "").strip()
    if not configured:
        return DryRunModel()
    try:
        return init_chat_model(configured)
    except ImportError as err:
        raise RuntimeError(
            f"MARLOW_MODEL is set to {configured!r} but its LangChain package is not installed: {err}"
        ) from err
