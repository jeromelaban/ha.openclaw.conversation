# OpenClaw Conversation

A Home Assistant custom integration that connects the Assist conversation and AI Task platforms to an OpenClaw OpenAI-compatible Gateway API.

## Important

This repository is a **HACS custom integration repository**, not a **Supervisor add-on repository**.

If you add it under **Settings > Add-ons > Add-on Store > Repositories**, Home Assistant will reject it with `not a valid add-on repository`.

Use **HACS > Integrations > Custom repositories** instead.

## Features

- Config flow for an OpenClaw-compatible `base_url`, bearer token, and default model
- Home Assistant `conversation` entity for Assist chat
- Home Assistant `ai_task` entity for structured data generation
- Optional Home Assistant LLM API tool exposure for home control workflows
- HACS-ready repository layout with validation workflows

## Scope

This first implementation targets OpenAI-compatible chat completions against an OpenClaw gateway. It intentionally focuses on conversation and structured AI task generation.

Not included yet:

- Speech-to-text
- Text-to-speech
- Image generation
- Provider-specific Responses API features

## Installation

### HACS custom repository

1. Open HACS in Home Assistant.
2. Go to `HACS > Integrations`.

3. Open the three-dot menu and choose `Custom repositories`.
4. Add this repository URL.
5. Choose category `Integration`.
6. Install `OpenClaw Conversation`.
7. Restart Home Assistant.
8. Add the integration from `Settings > Devices & services`.

### Manual

1. Copy `custom_components/openclaw_conversation` into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Add the integration from Settings > Devices & services.

## Configuration

During setup, provide:

- Gateway base URL, such as `http://openclaw.local:8080` or `https://gateway.example.internal/v1`
- Bearer token for the gateway
- Default model name

The integration normalizes the configured URL to end with `/v1` automatically.

## Development

- Main integration code: [custom_components/openclaw_conversation](custom_components/openclaw_conversation)
- Spec and research notes: [specs/001-initial-feature](specs/001-initial-feature)

## Troubleshooting

### `not a valid add-on repository`

Cause: the repo was added to the Supervisor add-on store instead of HACS.

Fix:

1. Remove the repository from the add-on store custom repositories list.
2. Open HACS.
3. Add the same GitHub URL as a custom repository with category `Integration`.
4. Install the integration from HACS.

## Security

OpenClaw gateway bearer tokens are operator-level credentials. Keep the gateway on a trusted network and avoid exposing it directly to the public internet.
