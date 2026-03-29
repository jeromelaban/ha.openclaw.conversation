"""AI Task support for OpenClaw Conversation."""

from __future__ import annotations

import logging
from json import JSONDecodeError

from homeassistant.components import ai_task, conversation
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util.json import json_loads

from . import OpenClawConversationConfigEntry
from .entity import OpenClawBaseEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass,
    config_entry: OpenClawConversationConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up OpenClaw AI Task entities."""
    async_add_entities([OpenClawAITaskEntity(config_entry)])


class OpenClawAITaskEntity(ai_task.AITaskEntity, OpenClawBaseEntity):
    """OpenClaw AI Task entity."""

    _attr_name = None
    _attr_supported_features = ai_task.AITaskEntityFeature.GENERATE_DATA

    def __init__(self, entry: OpenClawConversationConfigEntry) -> None:
        """Initialize the AI Task entity."""
        super().__init__(entry, "ai_task")

    async def _async_generate_data(
        self,
        task: ai_task.GenDataTask,
        chat_log: conversation.ChatLog,
    ) -> ai_task.GenDataTaskResult:
        """Handle a generate data request."""
        await self._async_handle_chat_log(chat_log, task.name, task.structure)

        if not isinstance(chat_log.content[-1], conversation.AssistantContent):
            raise HomeAssistantError(
                "Last content in chat log is not an AssistantContent"
            )

        text = chat_log.content[-1].content or ""
        if not task.structure:
            return ai_task.GenDataTaskResult(
                conversation_id=chat_log.conversation_id,
                data=text,
            )

        try:
            data = json_loads(text)
        except JSONDecodeError as err:
            _LOGGER.error("Failed to parse structured OpenClaw response: %s", err)
            raise HomeAssistantError(
                "OpenClaw returned invalid structured data"
            ) from err

        return ai_task.GenDataTaskResult(
            conversation_id=chat_log.conversation_id,
            data=data,
        )
