# paigram-impact-bot

Experimental PaiGram V6 application harness.

`paigram-impact-bot` composes the new PaiGram V6 runtime packages into an application-level harness. It does not depend on legacy `PaiGramBot` or `GramCore`, and it does not initialize PTB or start Telegram polling by itself.

This repository is not production-ready. Real plugin migration, configuration loading, and production startup commands are separate V6 phases.

## Harness Example

```python
from paigram_bot_telegram import TelegramRuntimeObjects

from paigram_impact_bot import ImpactBotHarnessConfig, build_impact_bot_harness


class FakeTelegramRuntime:
    def register_handler_declarations(self, declarations):
        return self


harness = build_impact_bot_harness(
    ImpactBotHarnessConfig(
        scanner_packages=("paigram_impact_bot",),
        telegram_runtime_objects=TelegramRuntimeObjects(runtime=FakeTelegramRuntime()),
    )
)
```

The harness builds a `paigram-bot-core` runtime, publishes injected Telegram runtime objects, and registers handler declarations onto `paigram-bot-telegram`.

## Built-In System Help POC

`system.help` is an in-repository proof-of-concept plugin. It is explicit opt-in and is not the final plugin discovery system.

```python
from paigram_bot_telegram import TelegramRuntimeObjects

from paigram_impact_bot import ImpactBotHarnessConfig, build_impact_bot_harness, with_system_help


class FakeTelegramRuntime:
    def register_handler_declarations(self, declarations):
        return self


config = with_system_help(
    ImpactBotHarnessConfig(
        scanner_packages=("paigram_impact_bot",),
        telegram_runtime_objects=TelegramRuntimeObjects(runtime=FakeTelegramRuntime()),
    )
)
harness = build_impact_bot_harness(config)
```

The POC contributes a `system.help` plugin manifest and a `/help` command declaration. The command callback remains platform-neutral and does not send Telegram messages directly.
