from asyncio import run

from paigram_bot_contracts import BotPlatform, PhotoResponse, TemplatePackage
from paigram_bot_core import RuntimePluginConfig, TemplateRuntimeObjects
from paigram_bot_telegram import TelegramRuntimeObjects

from paigram_impact_bot import ImpactBotHarnessConfig, with_system_rendered_help
from paigram_impact_bot.plugins.system_rendered_help import (
    HELP_IMAGE_TEMPLATE_PACKAGE,
    HELP_IMAGE_TEMPLATE_REF,
    RenderedHelpCommand,
    SYSTEM_RENDERED_HELP_PLUGIN,
    build_rendered_help_data,
)


class FakeTelegramRuntime:
    def register_handler_declarations(self, declarations):
        return self


class FakeImageRenderer:
    def __init__(self):
        self.calls = []

    async def render_png(self, template, data, *, viewport=None, selector=None, wait_until="load"):
        self.calls.append((template, data, viewport, selector, wait_until))
        return b"png"


def build_config(image_renderer=None):
    return ImpactBotHarnessConfig(
        scanner_packages=("paigram_impact_bot",),
        telegram_runtime_objects=TelegramRuntimeObjects(runtime=FakeTelegramRuntime()),
        template_runtime_objects=TemplateRuntimeObjects(image_renderer=image_renderer or FakeImageRenderer()),
    )


def test_system_rendered_help_plugin_manifest_shape():
    assert SYSTEM_RENDERED_HELP_PLUGIN.name == "system.help_image"
    assert SYSTEM_RENDERED_HELP_PLUGIN.scanner_packages == ["paigram_impact_bot.plugins"]
    assert SYSTEM_RENDERED_HELP_PLUGIN.platforms == [BotPlatform.TELEGRAM]
    assert SYSTEM_RENDERED_HELP_PLUGIN.capabilities == ["bot.help.rendered"]
    assert SYSTEM_RENDERED_HELP_PLUGIN.template_packages == [HELP_IMAGE_TEMPLATE_PACKAGE]


def test_help_image_template_package_shape():
    assert HELP_IMAGE_TEMPLATE_PACKAGE == TemplatePackage(
        namespace="system.help_image",
        package="paigram_impact_bot",
        template_path="templates/system_help",
        static_path=None,
    )


def test_build_rendered_help_data_is_deterministic():
    assert build_rendered_help_data() == {
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


def test_rendered_help_command_returns_photo_response():
    renderer = FakeImageRenderer()
    command = RenderedHelpCommand(renderer)

    result = run(command(object()))

    assert result == PhotoResponse(photo=b"png", filename="help.png")
    assert renderer.calls == [
        (
            HELP_IMAGE_TEMPLATE_REF,
            build_rendered_help_data(),
            {"width": 900, "height": 600},
            ".help-card",
            "load",
        )
    ]


def test_with_system_rendered_help_returns_new_config_without_mutating_input():
    image_renderer = FakeImageRenderer()
    config = build_config(image_renderer)

    configured = with_system_rendered_help(config)

    assert configured is not config
    assert config.plugin_config.enabled == []
    assert configured.plugin_config.enabled == ["system.help_image"]
    assert configured.plugins == (SYSTEM_RENDERED_HELP_PLUGIN,)
    assert config.plugins == ()
    assert len(configured.handler_declaration_groups) == 1
    declaration = configured.handler_declaration_groups[0].commands[0]
    assert declaration.command == "help_image"
    assert declaration.plugin_name == "system.help_image"
    assert declaration.description == "Show rendered Impact Bot help."


def test_with_system_rendered_help_is_idempotent_by_plugin_name_and_command():
    config = with_system_rendered_help(build_config())
    configured = with_system_rendered_help(config)

    assert configured.plugin_config.enabled == ["system.help_image"]
    assert configured.plugins == (SYSTEM_RENDERED_HELP_PLUGIN,)
    assert len(configured.handler_declaration_groups) == 1


def test_with_system_rendered_help_requires_image_renderer():
    config = ImpactBotHarnessConfig(
        scanner_packages=("paigram_impact_bot",),
        telegram_runtime_objects=TelegramRuntimeObjects(runtime=FakeTelegramRuntime()),
        template_runtime_objects=TemplateRuntimeObjects(),
    )

    try:
        with_system_rendered_help(config)
    except ValueError as error:
        assert str(error) == "system rendered help requires template_runtime_objects.image_renderer"
    else:
        raise AssertionError("expected ValueError")
