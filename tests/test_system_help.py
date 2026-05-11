from asyncio import run
from inspect import iscoroutinefunction

from paigram_bot_contracts import BotPlatform, TextResponse
from paigram_bot_core import RuntimePluginConfig
from paigram_bot_telegram import TelegramBotRuntime, TelegramRuntimeObjects

from paigram_impact_bot import ImpactBotHarnessConfig, build_impact_bot_harness, with_system_help
from paigram_impact_bot.plugins.system_help import (
    SYSTEM_HELP_HANDLERS,
    SYSTEM_HELP_PLUGIN,
    build_help_text,
    help_command,
)


class FakeTelegramRuntime:
    def register_handler_declarations(self, declarations):
        return self


class FakeTelegramApplication:
    def __init__(self):
        self.handlers = []

    def add_handler(self, handler):
        self.handlers.append(handler)


class FakeBot:
    def __init__(self):
        self.sent_messages = []

    async def send_message(self, *, chat_id, text):
        self.sent_messages.append({"chat_id": str(chat_id), "text": text})


class FakeTelegramContext:
    def __init__(self):
        self.bot = FakeBot()


class FakeUser:
    id = 12345
    full_name = "Tester"


class FakeChat:
    id = 67890


class FakeMessage:
    text = "/help"


class FakeUpdate:
    effective_user = FakeUser()
    effective_chat = FakeChat()
    effective_message = FakeMessage()


def test_system_help_plugin_manifest_shape():
    assert SYSTEM_HELP_PLUGIN.name == "system.help"
    assert SYSTEM_HELP_PLUGIN.scanner_packages == ["paigram_impact_bot.plugins"]
    assert SYSTEM_HELP_PLUGIN.platforms == [BotPlatform.TELEGRAM]
    assert SYSTEM_HELP_PLUGIN.capabilities == ["bot.help"]


def test_system_help_handler_declaration_shape():
    assert SYSTEM_HELP_HANDLERS.messages == ()
    assert len(SYSTEM_HELP_HANDLERS.commands) == 1

    declaration = SYSTEM_HELP_HANDLERS.commands[0]
    assert declaration.command == "help"
    assert declaration.callback is help_command
    assert declaration.platforms == (BotPlatform.TELEGRAM,)
    assert declaration.plugin_name == "system.help"
    assert declaration.description == "Show available Impact Bot commands."
    assert iscoroutinefunction(declaration.callback)


def test_build_help_text_is_deterministic():
    assert build_help_text() == "Impact Bot commands:\n/help - Show available Impact Bot commands."


def test_help_command_returns_text_response():
    result = run(help_command(object()))

    assert result == TextResponse(text=build_help_text())


def test_with_system_help_returns_new_config_without_mutating_input():
    telegram_objects = TelegramRuntimeObjects(runtime=FakeTelegramRuntime())
    config = ImpactBotHarnessConfig(
        scanner_packages=("paigram_impact_bot",),
        telegram_runtime_objects=telegram_objects,
    )

    configured = with_system_help(config)

    assert configured is not config
    assert config.plugin_config.enabled == []
    assert configured.plugin_config.enabled == ["system.help"]
    assert configured.plugin_config is not config.plugin_config
    assert config.plugins == ()
    assert config.handler_declaration_groups == ()
    assert configured.plugins == (SYSTEM_HELP_PLUGIN,)
    assert configured.handler_declaration_groups == (SYSTEM_HELP_HANDLERS,)
    assert configured.scanner_packages == config.scanner_packages
    assert configured.telegram_runtime_objects is telegram_objects


def test_with_system_help_is_idempotent_for_plugin_name_and_handler_group_identity():
    telegram_objects = TelegramRuntimeObjects(runtime=FakeTelegramRuntime())
    config = ImpactBotHarnessConfig(
        scanner_packages=("paigram_impact_bot",),
        plugins=(SYSTEM_HELP_PLUGIN,),
        handler_declaration_groups=(SYSTEM_HELP_HANDLERS,),
        telegram_runtime_objects=telegram_objects,
    )

    configured = with_system_help(config)

    assert configured.plugins == (SYSTEM_HELP_PLUGIN,)
    assert configured.handler_declaration_groups == (SYSTEM_HELP_HANDLERS,)


def test_with_system_help_preserves_enabled_plugins_without_duplicates():
    telegram_objects = TelegramRuntimeObjects(runtime=FakeTelegramRuntime())
    plugin_config = RuntimePluginConfig(enabled=["custom.plugin", "system.help"])
    config = ImpactBotHarnessConfig(
        scanner_packages=("paigram_impact_bot",),
        plugin_config=plugin_config,
        plugins=(SYSTEM_HELP_PLUGIN,),
        handler_declaration_groups=(SYSTEM_HELP_HANDLERS,),
        telegram_runtime_objects=telegram_objects,
    )

    configured = with_system_help(config)

    assert configured.plugin_config is plugin_config
    assert configured.plugin_config.enabled == ["custom.plugin", "system.help"]


def test_harness_registers_system_help_command(monkeypatch):
    application = FakeTelegramApplication()
    telegram_runtime = TelegramBotRuntime(application)
    telegram_objects = TelegramRuntimeObjects(application=application, runtime=telegram_runtime)

    class FakeCommandHandler:
        def __init__(self, command, callback):
            self.command = command
            self.callback = callback

    monkeypatch.setattr("paigram_bot_telegram.handlers.CommandHandler", FakeCommandHandler)

    config = with_system_help(
        ImpactBotHarnessConfig(
            scanner_packages=("paigram_impact_bot",),
            telegram_runtime_objects=telegram_objects,
        )
    )

    harness = build_impact_bot_harness(config)

    assert harness.bot_runtime.handler_declarations.commands == SYSTEM_HELP_HANDLERS.commands
    assert harness.bot_runtime.selected_plugins.names == ["system.help"]
    assert len(application.handlers) == 1
    assert application.handlers[0].command == "help"

    telegram_context = FakeTelegramContext()
    run(application.handlers[0].callback(FakeUpdate(), telegram_context))

    assert telegram_context.bot.sent_messages == [
        {"chat_id": "67890", "text": build_help_text()},
    ]
