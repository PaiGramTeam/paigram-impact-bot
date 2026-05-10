from dataclasses import replace

from paigram_bot_contracts import PluginHandlerDeclarations, PluginPackage

from paigram_impact_bot.config import ImpactBotHarnessConfig
from paigram_impact_bot.plugins.system_help import SYSTEM_HELP_HANDLERS, SYSTEM_HELP_PLUGIN


def _append_plugin_once(plugins: tuple[PluginPackage, ...], plugin: PluginPackage) -> tuple[PluginPackage, ...]:
    if any(existing.name == plugin.name for existing in plugins):
        return plugins
    return (*plugins, plugin)


def _append_handler_group_once(
    groups: tuple[PluginHandlerDeclarations, ...],
    group: PluginHandlerDeclarations,
) -> tuple[PluginHandlerDeclarations, ...]:
    if any(existing is group for existing in groups):
        return groups
    return (*groups, group)


def with_system_help(config: ImpactBotHarnessConfig) -> ImpactBotHarnessConfig:
    plugins = _append_plugin_once(config.plugins, SYSTEM_HELP_PLUGIN)
    groups = _append_handler_group_once(config.handler_declaration_groups, SYSTEM_HELP_HANDLERS)
    return replace(config, plugins=plugins, handler_declaration_groups=groups)
