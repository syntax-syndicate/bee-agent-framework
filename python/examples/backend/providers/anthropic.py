import asyncio
from typing import Final

from pydantic import BaseModel, Field

from beeai_framework.adapters.anthropic import AnthropicChatModel
from beeai_framework.backend import ChatModel, ChatModelNewTokenEvent, UserMessage
from beeai_framework.emitter import EventMeta
from beeai_framework.errors import AbortError
from beeai_framework.parsers.field import ParserField
from beeai_framework.parsers.line_prefix import LinePrefixParser, LinePrefixParserNode
from beeai_framework.utils import AbortSignal

MODEL_NAME: Final[str] = "claude-3-haiku-20240307"


async def anthropic_from_name() -> None:
    llm = ChatModel.from_name(f"anthropic:{MODEL_NAME}")
    user_message = UserMessage("what states are part of New England?")
    response = await llm.create(messages=[user_message])
    print(response.get_text_content())


async def anthropic_sync() -> None:
    llm = AnthropicChatModel(MODEL_NAME)
    user_message = UserMessage("what is the capital of Massachusetts?")
    response = await llm.create(messages=[user_message])
    print(response.get_text_content())


async def anthropic_stream() -> None:
    llm = AnthropicChatModel(MODEL_NAME)
    user_message = UserMessage("How many islands make up the country of Cape Verde?")
    response = await llm.create(messages=[user_message], stream=True)
    print(response.get_text_content())


async def anthropic_stream_abort() -> None:
    llm = AnthropicChatModel(MODEL_NAME)
    user_message = UserMessage("What is the smallest of the Cape Verde islands?")

    try:
        response = await llm.create(messages=[user_message], stream=True, abort_signal=AbortSignal.timeout(0.5))

        if response is not None:
            print(response.get_text_content())
        else:
            print("No response returned.")
    except AbortError as err:
        print(f"Aborted: {err}")


async def anthropic_structure() -> None:
    class TestSchema(BaseModel):
        answer: str = Field(description="your final answer")

    llm = AnthropicChatModel(MODEL_NAME)
    user_message = UserMessage("How many islands make up the country of Cape Verde?")
    response = await llm.create_structure(schema=TestSchema, messages=[user_message])
    print(response.object)


async def anthropic_stream_parser() -> None:
    llm = AnthropicChatModel(MODEL_NAME)

    parser = LinePrefixParser(
        nodes={
            "test": LinePrefixParserNode(
                prefix="Prefix: ",
                field=ParserField.from_type(str),
                is_start=True,
                is_end=True,
            )
        }
    )

    async def on_new_token(data: ChatModelNewTokenEvent, event: EventMeta) -> None:
        await parser.add(chunk=data.value.get_text_content())

    user_message = UserMessage("Produce 3 lines each starting with 'Prefix: ' followed by a sentence and a new line.")
    await llm.create(messages=[user_message], stream=True).observe(
        lambda emitter: emitter.on("new_token", on_new_token)
    )
    result = await parser.end()
    print(result)


async def main() -> None:
    print("*" * 10, "anthropic_from_name")
    await anthropic_from_name()
    print("*" * 10, "anthropic_sync")
    await anthropic_sync()
    print("*" * 10, "anthropic_stream")
    await anthropic_stream()
    print("*" * 10, "anthropic_stream_abort")
    await anthropic_stream_abort()
    print("*" * 10, "anthropic_structure")
    await anthropic_structure()
    print("*" * 10, "anthropic_stream_parser")
    await anthropic_stream_parser()


if __name__ == "__main__":
    asyncio.run(main())
