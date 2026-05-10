# paigram-impact-bot

Experimental PaiGram V6 application harness.

`paigram-impact-bot` composes the new PaiGram V6 runtime packages into an application-level harness. It does not depend on legacy `PaiGramBot` or `GramCore`, and it does not initialize PTB or start Telegram polling by itself.

This repository is not production-ready. Real plugin migration, configuration loading, and production startup commands are later V6 phases.

## Harness Example

```python
from paigram_bot_telegram import TelegramRuntimeObjects

from paigram_impact_bot import ImpactBotHarnessConfig, build_impact_bot_harness


harness = build_impact_bot_harness(
    ImpactBotHarnessConfig(
        scanner_packages=("paigram_impact_bot",),
        telegram_runtime_objects=TelegramRuntimeObjects(runtime=telegram_runtime),
    )
)
```

The harness builds a `paigram-bot-core` runtime, publishes Telegram runtime objects, and registers handler declarations onto `paigram-bot-telegram`.
