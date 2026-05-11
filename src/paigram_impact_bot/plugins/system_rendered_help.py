from typing import Any, Protocol

from paigram_bot_contracts import (
    BotPlatform,
    CommandHandlerDeclaration,
    PhotoResponse,
    PluginHandlerDeclarations,
    PluginPackage,
    TemplatePackage,
)
from paigram_template_runtime import TemplateRef


class HelpImageRenderer(Protocol):
    async def render_png(
        self,
        template: TemplateRef,
        data: dict[str, Any],
        *,
        viewport: dict[str, int] | None = None,
        selector: str | None = None,
        wait_until: str = "load",
    ) -> bytes: ...


HELP_IMAGE_TEMPLATE_PACKAGE = TemplatePackage(
    namespace="system.help_image",
    package="paigram_impact_bot",
    template_path="templates/system_help",
    static_path=None,
)
HELP_IMAGE_TEMPLATE_REF = TemplateRef(namespace="system.help_image", name="help.html")
HELP_IMAGE_VIEWPORT = {"width": 900, "height": 600}

SYSTEM_RENDERED_HELP_PLUGIN = PluginPackage(
    name="system.help_image",
    scanner_packages=["paigram_impact_bot.plugins"],
    platforms=[BotPlatform.TELEGRAM],
    capabilities=["bot.help.rendered"],
    template_packages=[HELP_IMAGE_TEMPLATE_PACKAGE],
)


def build_rendered_help_data() -> dict[str, object]:
    return {
        "title": "Impact Bot",
        "subtitle": "PaiGram V6 rendered help preview",
        "commands": [
            {"command": "/help", "description": "Show available Impact Bot commands."},
            {"command": "/start", "description": "Start the Impact Bot."},
            {"command": "/ping", "description": "Check whether Impact Bot is online."},
            {"command": "/privacy", "description": "Show the PaiGram privacy policy."},
            {"command": "/help_image", "description": "Show rendered Impact Bot help."},
        ],
    }


class RenderedHelpCommand:
    def __init__(self, image_renderer: HelpImageRenderer):
        self.image_renderer = image_renderer

    async def __call__(self, context) -> PhotoResponse:
        image = await self.image_renderer.render_png(
            HELP_IMAGE_TEMPLATE_REF,
            build_rendered_help_data(),
            viewport=HELP_IMAGE_VIEWPORT,
            selector=".help-card",
        )
        return PhotoResponse(photo=image, filename="help.png")


def build_system_rendered_help_handlers(image_renderer: HelpImageRenderer) -> PluginHandlerDeclarations:
    return PluginHandlerDeclarations(
        commands=(
            CommandHandlerDeclaration(
                command="help_image",
                callback=RenderedHelpCommand(image_renderer),
                platforms=(BotPlatform.TELEGRAM,),
                plugin_name="system.help_image",
                description="Show rendered Impact Bot help.",
            ),
        )
    )
