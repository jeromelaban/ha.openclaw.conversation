# Progress

- Spec ID: 001-initial-feature
- Last updated: 2026-03-29
- Status: Implemented (scaffold plus initial CI fixes)

## Completed

1. Confirmed the workspace had no prior local spec template to inherit.
2. Researched the OpenClaw OpenAI-compatible Gateway API.
3. Reviewed the upstream Home Assistant `openai_conversation` integration structure and behavior.
4. Reviewed Home Assistant custom integration manifest guidance.
5. Reviewed HACS custom integration repository requirements and GitHub Action guidance.
6. Drafted the initial feature spec.
7. Implemented the initial custom integration scaffold under `custom_components/openclaw_conversation/`.
8. Added repository metadata for HACS and contributor workflows.
9. Added GitHub Actions for HACS validation, hassfest, and Ruff linting.
10. Investigated the latest failing GitHub Actions runs for Ruff, hassfest, and HACS validation.
11. Fixed Ruff issues in the integration modules by organizing imports, wrapping long lines, and correcting a type reference.
12. Fixed Home Assistant manifest validation by adding missing manifest fields and correcting the `iot_class` value.
13. Added a config-entry-only schema to match the integration's setup model.
14. Corrected `hacs.json` content to match the validator's accepted keys.

## Decisions Made

1. Use `specs/001-initial-feature/` as the numbered Speckit-style folder.
2. Treat the repository target as a **HACS custom integration repository**, not a Supervisor add-on repository.
3. Keep the initial product scope focused on LLM conversation use cases.
4. Defer STT, TTS, and image-generation support until OpenClaw compatibility is verified.
5. Use a configurable OpenAI-compatible `base_url` as the core differentiator from upstream `openai_conversation`.
6. Use the OpenAI-compatible Chat Completions API first to keep the initial implementation smaller and easier to validate.
7. Ship one config entry that exposes one conversation entity and one AI Task entity, with advanced model settings managed through options.
8. Treat HACS repository description and repository topics as release-blocking publication metadata that must be configured in GitHub, not in-repo files.

## Next Steps

1. Add repository description and valid repository topics in GitHub so HACS repository validation can pass.
2. Add brand assets so HACS validation no longer needs the current `brands` ignore in CI.
3. Decide whether to fetch model choices dynamically in the config/options flow instead of keeping model entry as free text.
4. Evaluate whether to add OpenAI Responses API support after OpenClaw compatibility is confirmed.
5. Add integration tests once a Home Assistant custom-component test harness is introduced.

## Known Open Questions

1. SSL/self-signed certificate handling is still unspecified.
2. OpenClaw compatibility for STT/TTS/images is unverified.
3. Long-term upstream sync strategy with Home Assistant core is still undefined.
4. Brand asset strategy for public HACS publication is still unfinished.
5. The exact repository topic set to use for HACS publication is still not decided.

## Exit Criteria For This Spec Phase

- `spec.md` reflects the intended initial feature scope.
- research findings are captured in `research.md`.
- unresolved scope decisions are visible before coding begins.

## Implementation Outcome

- A HACS-compatible repository scaffold now exists.
- The custom integration includes config flow, options flow, conversation support, and AI Task support.
- Basic repository automation is present for validation and linting.
- The codebase now includes the initial round of CI-driven fixes for Ruff, hassfest manifest validation, and HACS metadata file validation.
- Remaining HACS failures are outside the codebase and must be resolved in GitHub repository settings.
