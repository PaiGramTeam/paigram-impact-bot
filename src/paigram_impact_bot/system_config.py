from dataclasses import replace

from paigram_bot_core import RuntimePluginConfig
from paigram_bot_contracts import PluginHandlerDeclarations, PluginPackage

from paigram_impact_bot.config import ImpactBotHarnessConfig
from paigram_impact_bot.plugins.system_help import SYSTEM_HELP_HANDLERS, SYSTEM_HELP_PLUGIN
from paigram_impact_bot.plugins.system_start import SYSTEM_START_HANDLERS, SYSTEM_START_PLUGIN


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


def _enable_plugin_once(plugin_config: RuntimePluginConfig, plugin_name: str) -> RuntimePluginConfig:
    if plugin_name in plugin_config.enabled:
        return plugin_config
    return RuntimePluginConfig(enabled=[*plugin_config.enabled, plugin_name])


def _with_system_plugin(
    config: ImpactBotHarnessConfig,
    plugin: PluginPackage,
    handlers: PluginHandlerDeclarations,
) -> ImpactBotHarnessConfig:
    plugins = _append_plugin_once(config.plugins, plugin)
    groups = _append_handler_group_once(config.handler_declaration_groups, handlers)
    plugin_config = _enable_plugin_once(config.plugin_config, plugin.name)
    return replace(
        config,
        plugin_config=plugin_config,
        plugins=plugins,
        handler_declaration_groups=groups,
    )


def with_system_help(config: ImpactBotHarnessConfig) -> ImpactBotHarnessConfig:
    return _with_system_plugin(config, SYSTEM_HELP_PLUGIN, SYSTEM_HELP_HANDLERS)


def with_system_start(config: ImpactBotHarnessConfig) -> ImpactBotHarnessConfig:
    return _with_system_plugin(config, SYSTEM_START_PLUGIN, SYSTEM_START_HANDLERS)


def with_builtin_system_plugins(config: ImpactBotHarnessConfig) -> ImpactBotHarnessConfig:
    return with_system_start(with_system_help(config))
