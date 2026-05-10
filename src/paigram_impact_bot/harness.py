from dataclasses import dataclass

from paigram_bot_core import BotRuntime, BotRuntimeBuilder
from paigram_bot_telegram import TelegramBotRuntime, TelegramRuntimeObjects, build_telegram_application

from paigram_impact_bot.config import ImpactBotHarnessConfig


@dataclass(frozen=True)
class ImpactBotHarness:
    bot_runtime: BotRuntime
    telegram_runtime: TelegramBotRuntime
    telegram_objects: TelegramRuntimeObjects

    @property
    def handler_declarations(self):
        return self.bot_runtime.handler_declarations

    @property
    def application(self):
        return self.bot_runtime.application


def _build_telegram_objects(config: ImpactBotHarnessConfig) -> TelegramRuntimeObjects:
    if config.telegram_runtime_objects is not None:
        return config.telegram_runtime_objects
    application = build_telegram_application(config.telegram_config)
    runtime = TelegramBotRuntime(application)
    return TelegramRuntimeObjects(config=config.telegram_config, application=application, runtime=runtime)


def build_impact_bot_harness(config: ImpactBotHarnessConfig) -> ImpactBotHarness:
    telegram_objects = _build_telegram_objects(config)
    telegram_runtime = telegram_objects.runtime

    builder = BotRuntimeBuilder()
    builder.set_plugin_config(config.plugin_config)
    builder.add_plugins(list(config.plugins))
    for package in config.scanner_packages:
        builder.add_scanner_package(package)
    builder.add_handler_declaration_groups(config.handler_declaration_groups)
    for declaration in config.command_handler_declarations:
        builder.add_command_handler_declaration(declaration)
    for declaration in config.message_handler_declarations:
        builder.add_message_handler_declaration(declaration)
    if config.template_runtime_objects is not None:
        builder.set_template_runtime(config.template_runtime_objects)
    if config.resource_runtime_objects is not None:
        builder.set_resource_runtime(config.resource_runtime_objects)
    if config.platform_runtime_objects is not None:
        builder.set_platform_runtime(config.platform_runtime_objects)
    builder.add_external_objects(telegram_objects.all_objects())
    builder.add_external_objects(config.external_objects)

    bot_runtime = builder.build()
    telegram_runtime.register_handler_declarations(bot_runtime.handler_declarations)
    return ImpactBotHarness(
        bot_runtime=bot_runtime,
        telegram_runtime=telegram_runtime,
        telegram_objects=telegram_objects,
    )
