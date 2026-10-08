from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

from .llm import build_model

PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You draft replies for the Marlow Maps support desk. The people writing in are developers at "
            "delivery, courier and field-service companies who are integrating the geocoding and routing API. "
            "Write two to four plain sentences that answer the ticket using the FAQ answer you are given, "
            "keep every endpoint, header, number and value exactly as the FAQ states it, and do not add a "
            "greeting or a sign-off. A member of staff reads every draft before it is sent.",
        ),
        ("human", "Ticket: {question}\n\nFAQ question: {faq_question}\nAnswer: {answer}"),
    ]
)


def build_chain(model: BaseChatModel | None = None) -> Runnable:
    return PROMPT | (model or build_model()) | StrOutputParser()
