from collections.abc import MutableMapping

from paigram_bot_contracts import BotPlatform, CommandHandlerDeclaration, PluginHandlerDeclarations, PluginPackage


HELP_TEXT = "Impact Bot commands:\n/help - Show available Impact Bot commands."

SYSTEM_HELP_PLUGIN = PluginPackage(
    name="system.help",
    scanner_packages=["paigram_impact_bot.plugins"],
    platforms=[BotPlatform.TELEGRAM],
    capabilities=["bot.help"],
)


def build_help_text() -> str:
    return HELP_TEXT


async def help_command(context) -> None:
    help_text = build_help_text()
    metadata = getattr(context, "metadata", None)
    if isinstance(metadata, MutableMapping):
        metadata["system.help.text"] = help_text
    return None


SYSTEM_HELP_HANDLERS = PluginHandlerDeclarations(
    commands=(
        CommandHandlerDeclaration(
            command="help",
            callback=help_command,
            platforms=(BotPlatform.TELEGRAM,),
            plugin_name="system.help",
            description="Show available Impact Bot commands.",
        ),
    )
)
