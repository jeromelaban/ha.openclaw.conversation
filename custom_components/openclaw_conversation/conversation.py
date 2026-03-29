"""Conversation support for OpenClaw Conversation."""

from __future__ import annotations

from typing import Literal

from homeassistant.components import conversation
from homeassistant.const import CONF_LLM_HASS_API, CONF_PROMPT, MATCH_ALL
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import OpenClawConversationConfigEntry
from .const import DOMAIN
from .entity import OpenClawBaseEntity


async def async_setup_entry(
    hass,
    config_entry: OpenClawConversationConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up OpenClaw conversation entities."""
    async_add_entities([OpenClawConversationEntity(config_entry)])


class OpenClawConversationEntity(OpenClawBaseEntity, conversation.ConversationEntity):
    """OpenClaw conversation agent."""

    _attr_name = None

    def __init__(self, entry: OpenClawConversationConfigEntry) -> None:
        """Initialize the conversation agent."""
        super().__init__(entry, "conversation")
        if self.settings.get(CONF_LLM_HASS_API):
            self._attr_supported_features = (
                conversation.ConversationEntityFeature.CONTROL
            )

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        """Return the list of supported languages."""
        return MATCH_ALL

    async def _async_handle_message(
        self,
        user_input: conversation.ConversationInput,
        chat_log: conversation.ChatLog,
    ) -> conversation.ConversationResult:
        """Handle a user message."""
        try:
            await chat_log.async_provide_llm_data(
                user_input.as_llm_context(DOMAIN),
                self.settings.get(CONF_LLM_HASS_API),
                self.settings.get(CONF_PROMPT),
                user_input.extra_system_prompt,
            )
        except conversation.ConverseError as err:
            return err.as_conversation_result()

        await self._async_handle_chat_log(chat_log)
        return conversation.async_get_result_from_chat_log(user_input, chat_log)
