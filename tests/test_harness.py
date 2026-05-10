from paigram_bot_contracts import BotPlatform, CommandHandlerDeclaration, PluginHandlerDeclarations, TextMessageHandlerDeclaration
from paigram_bot_telegram import TelegramBotRuntime, TelegramRuntimeObjects

from paigram_impact_bot import ImpactBotHarness, ImpactBotHarnessConfig, build_impact_bot_harness


class FakeTelegramApplication:
    def __init__(self):
        self.handlers = []
        self.lifecycle_calls = []

    def add_handler(self, handler):
        self.handlers.append(handler)

    async def initialize(self):
        self.lifecycle_calls.append("initialize")

    async def start(self):
        self.lifecycle_calls.append("start")

    async def stop(self):
        self.lifecycle_calls.append("stop")

    async def shutdown(self):
        self.lifecycle_calls.append("shutdown")


async def start_callback(context):
    return None


async def ping_callback(context):
    return None


async def discord_callback(context):
    return None


async def text_callback(context):
    return None


async def discord_text_callback(context):
    return None


def build_injected_telegram_objects():
    application = FakeTelegramApplication()
    runtime = TelegramBotRuntime(application)
    return application, runtime, TelegramRuntimeObjects(application=application, runtime=runtime)


def test_build_impact_bot_harness_registers_handler_declarations(monkeypatch):
    application, runtime, telegram_objects = build_injected_telegram_objects()
    monkeypatch.setattr(
        "paigram_bot_telegram.runtime.build_command_handler",
        lambda command, callback: ("command", command, callback),
    )
    monkeypatch.setattr(
        "paigram_bot_telegram.runtime.build_message_handler",
        lambda callback: ("message", callback),
    )
    declarations = PluginHandlerDeclarations(
        commands=(
            CommandHandlerDeclaration(command="start", callback=start_callback),
            CommandHandlerDeclaration(command="ping", callback=ping_callback, platforms=(BotPlatform.TELEGRAM,)),
            CommandHandlerDeclaration(command="discord", callback=discord_callback, platforms=(BotPlatform.DISCORD,)),
        ),
        messages=(
            TextMessageHandlerDeclaration(name="text", callback=text_callback),
            TextMessageHandlerDeclaration(name="discord_text", callback=discord_text_callback, platforms=(BotPlatform.DISCORD,)),
        ),
    )

    harness = build_impact_bot_harness(
        ImpactBotHarnessConfig(
            scanner_packages=("paigram_impact_bot",),
            telegram_runtime_objects=telegram_objects,
            handler_declaration_groups=(declarations,),
        )
    )

    assert isinstance(harness, ImpactBotHarness)
    assert harness.telegram_runtime is runtime
    assert harness.telegram_objects is telegram_objects
    assert harness.bot_runtime.handler_declarations.commands == declarations.commands
    assert harness.bot_runtime.handler_declarations.messages == declarations.messages
    assert application.handlers == [
        ("command", "start", start_callback),
        ("command", "ping", ping_callback),
        ("message", text_callback),
    ]
    assert application.lifecycle_calls == []


def test_build_impact_bot_harness_preserves_scanner_packages_and_external_objects():
    _, _, telegram_objects = build_injected_telegram_objects()
    marker = object()

    harness = build_impact_bot_harness(
        ImpactBotHarnessConfig(
            scanner_packages=("paigram_impact_bot", "paigram_impact_bot"),
            telegram_runtime_objects=telegram_objects,
            external_objects=(marker,),
        )
    )

    assert harness.bot_runtime.scanner_packages == ["paigram_impact_bot"]
    assert marker in harness.bot_runtime.external_objects
    assert telegram_objects.runtime in harness.bot_runtime.external_objects


def test_build_impact_bot_harness_exposes_convenience_properties():
    _, _, telegram_objects = build_injected_telegram_objects()

    harness = build_impact_bot_harness(
        ImpactBotHarnessConfig(
            scanner_packages=("paigram_impact_bot",),
            telegram_runtime_objects=telegram_objects,
        )
    )

    assert harness.application is harness.bot_runtime.application
    assert harness.handler_declarations is harness.bot_runtime.handler_declarations
