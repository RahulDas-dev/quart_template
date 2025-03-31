import asyncio
import logging
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar

from pydantic_ai import Agent, BinaryContent, ModelRetry
from pydantic_ai.models.openai import OpenAIModel
from quart import Quart

from .prompts import PAGE_TEMPLATE, SYSTEM_MESSAGE_1, SYSTEM_MESSAGE_2, USER_MESSAGE_1
from .schemas import Invoice, InvoiceData
from .utility import image_to_byte_string, sorted_images

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class InvoiceSeviceConfig:
    model1_name: str = field(default="us.meta.llama3-2-90b-instruct-v1:0")
    model2_name: str = field(default="gpt-4o")
    max_call_min: int = field(default=10)

    @classmethod
    def init_from_app(cls, app: Quart) -> "InvoiceSeviceConfig":
        model1_name_ = app.config.get("MODEL1_NAME", "")
        model2_name_ = app.config.get("MODEL2_NAME", "")
        max_call_min_ = app.config.get("MAX_CALL_MIN", 10)
        return InvoiceSeviceConfig(model1_name=model1_name_, model2_name=model2_name_, max_call_min=max_call_min_)


class InvoiceService:
    config: ClassVar[InvoiceSeviceConfig]
    agent1: Agent[None, str]
    agent2: Agent[None, Invoice]

    @classmethod
    def configure_from_app(cls, app: Quart) -> None:
        config_ = InvoiceSeviceConfig.init_from_app(app)
        cls.set_config(config_)

    @classmethod
    def set_config(cls, config: InvoiceSeviceConfig) -> None:
        cls.config = config

    @classmethod
    def setup_agents(cls) -> None:
        agent1 = Agent(
            # model=BedrockConverseModel(
            #     model_name=cls.config.model1_name,
            #     provider=BedrockProvider(**get_secret_keys()),
            # ),
            model=OpenAIModel(cls.config.model2_name),
            system_prompt=SYSTEM_MESSAGE_1,
            result_type=str,
            model_settings={"temperature": 0},
        )

        agent2 = Agent(
            model=OpenAIModel(cls.config.model2_name),
            system_prompt=SYSTEM_MESSAGE_2,
            result_type=Invoice,
            model_settings={"temperature": 0},
        )

        @agent2.result_validator
        async def validate_result(result: Any) -> Any:
            if isinstance(result, Invoice):
                return result
            return ModelRetry("Final result Format is not Correct ")

        cls.agent1 = agent1
        cls.agent2 = agent2

    @classmethod
    async def _get_agent1_response(cls, img_path: Path, page_no: int) -> tuple[str, int]:
        async with cls.semaphore:
            logger.info(f"Agent1 Processing Page : {img_path.name}")
            img_byte, mimetype = image_to_byte_string(img_path.resolve())
            input_msg = [
                USER_MESSAGE_1,
                BinaryContent(data=img_byte, media_type=mimetype),
            ]
            result1 = await cls.agent1.run(input_msg)
            response = PAGE_TEMPLATE.substitute(page_no=page_no, page_content=result1.data)
            return response, page_no

    @classmethod
    async def _get_agent2_response(cls, content: str, page_no: int) -> Invoice:
        async with cls.semaphore:
            logger.info(f"Agent2 Processing Page : {page_no}")
            result2 = await cls.agent2.run([content])
            return result2.data

    @classmethod
    async def _process_response(cls, agent1_response: list[tuple[str, int]]) -> AsyncGenerator[tuple, None]:
        agent1_response = sorted(agent1_response, key=lambda x: x[1])
        for response, page_no in agent1_response:
            yield response, page_no

    @classmethod
    async def run(cls, image_dir: str | Path) -> InvoiceData:
        cls.setup_agents()
        cls.semaphore = asyncio.Semaphore(cls.config.max_call_min)
        pdf_content, agent1_task = [], []
        async for img_path, page_no in sorted_images(image_dir):
            agent1_task.append(cls._get_agent1_response(img_path, page_no))
        pdf_content = await asyncio.gather(*agent1_task)
        logger.info(f"Agent1 has completed the processing of {len(pdf_content)} pages")
        final_result, agent2_task = [], []
        cls.semaphore = asyncio.Semaphore(cls.config.max_call_min)
        async for content, p_no in cls._process_response(pdf_content):
            agent2_task.append(cls._get_agent2_response(content, p_no))
        final_result = await asyncio.gather(*agent2_task)
        final_result = [result for result in final_result if isinstance(result, Invoice)]
        return InvoiceData(details=final_result)
