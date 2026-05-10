from dataclasses import dataclass, field

from paigram_bot_contracts import CommandHandlerDeclaration, PluginHandlerDeclarations, PluginPackage, TextMessageHandlerDeclaration
from paigram_bot_core import PlatformRuntimeObjects, ResourceRuntimeObjects, RuntimePluginConfig, TemplateRuntimeObjects
from paigram_bot_telegram import TelegramRuntimeConfig, TelegramRuntimeObjects


def _clean_scanner_packages(packages: tuple[str, ...]) -> tuple[str, ...]:
    cleaned = tuple(package.strip() for package in packages if package.strip())
    if not cleaned:
        raise ValueError("scanner_packages must contain at least one package")
    return cleaned


@dataclass(frozen=True)
class ImpactBotHarnessConfig:
    scanner_packages: tuple[str, ...]
    plugins: tuple[PluginPackage, ...] = field(default_factory=tuple)
    plugin_config: RuntimePluginConfig = field(default_factory=RuntimePluginConfig)
    handler_declaration_groups: tuple[PluginHandlerDeclarations, ...] = field(default_factory=tuple)
    command_handler_declarations: tuple[CommandHandlerDeclaration, ...] = field(default_factory=tuple)
    message_handler_declarations: tuple[TextMessageHandlerDeclaration, ...] = field(default_factory=tuple)
    telegram_config: TelegramRuntimeConfig | None = None
    telegram_runtime_objects: TelegramRuntimeObjects | None = None
    template_runtime_objects: TemplateRuntimeObjects | None = None
    resource_runtime_objects: ResourceRuntimeObjects | None = None
    platform_runtime_objects: PlatformRuntimeObjects | None = None
    external_objects: tuple[object, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        object.__setattr__(self, "scanner_packages", _clean_scanner_packages(self.scanner_packages))
        if self.telegram_config is not None and self.telegram_runtime_objects is not None:
            raise ValueError("telegram_config and telegram_runtime_objects are mutually exclusive")
        if self.telegram_config is None and self.telegram_runtime_objects is None:
            raise ValueError("telegram runtime configuration is required")
        if self.telegram_runtime_objects is not None and self.telegram_runtime_objects.runtime is None:
            raise ValueError("telegram runtime objects must include runtime")
