from asyncio import run
from inspect import iscoroutinefunction

from paigram_bot_contracts import BotPlatform
from paigram_bot_telegram import TelegramRuntimeObjects

from paigram_impact_bot import ImpactBotHarnessConfig, with_system_help
from paigram_impact_bot.plugins.system_help import (
    SYSTEM_HELP_HANDLERS,
    SYSTEM_HELP_PLUGIN,
    build_help_text,
    help_command,
)


class MutableMetadataContext:
    def __init__(self):
        self.metadata = {}


class NoMetadataContext:
    pass


class FakeTelegramRuntime:
    def register_handler_declarations(self, declarations):
        return self


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


def test_help_command_writes_help_text_to_mutable_metadata():
    context = MutableMetadataContext()

    result = run(help_command(context))

    assert result is None
    assert context.metadata == {"system.help.text": build_help_text()}


def test_help_command_ignores_context_without_metadata():
    result = run(help_command(NoMetadataContext()))

    assert result is None


def test_with_system_help_returns_new_config_without_mutating_input():
    telegram_objects = TelegramRuntimeObjects(runtime=FakeTelegramRuntime())
    config = ImpactBotHarnessConfig(
        scanner_packages=("paigram_impact_bot",),
        telegram_runtime_objects=telegram_objects,
    )

    configured = with_system_help(config)

    assert configured is not config
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
