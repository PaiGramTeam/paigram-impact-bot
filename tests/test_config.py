import pytest
from paigram_bot_telegram import TelegramRuntimeConfig, TelegramRuntimeObjects

from paigram_impact_bot import ImpactBotHarnessConfig


class FakeTelegramRuntime:
    def register_handler_declarations(self, declarations):
        return self


def test_harness_config_strips_scanner_packages():
    config = ImpactBotHarnessConfig(
        scanner_packages=(" paigram_impact_bot ", ""),
        telegram_runtime_objects=TelegramRuntimeObjects(runtime=FakeTelegramRuntime()),
    )

    assert config.scanner_packages == ("paigram_impact_bot",)


def test_harness_config_rejects_missing_scanner_packages():
    with pytest.raises(ValueError, match="scanner_packages must contain at least one package"):
        ImpactBotHarnessConfig(
            scanner_packages=("   ",),
            telegram_runtime_objects=TelegramRuntimeObjects(runtime=FakeTelegramRuntime()),
        )


def test_harness_config_requires_telegram_runtime_configuration():
    with pytest.raises(ValueError, match="telegram runtime configuration is required"):
        ImpactBotHarnessConfig(scanner_packages=("paigram_impact_bot",))


def test_harness_config_rejects_both_telegram_inputs():
    with pytest.raises(ValueError, match="telegram_config and telegram_runtime_objects are mutually exclusive"):
        ImpactBotHarnessConfig(
            scanner_packages=("paigram_impact_bot",),
            telegram_config=TelegramRuntimeConfig(token="123:abc"),
            telegram_runtime_objects=TelegramRuntimeObjects(runtime=FakeTelegramRuntime()),
        )


def test_harness_config_rejects_runtime_objects_without_runtime():
    with pytest.raises(ValueError, match="telegram runtime objects must include runtime"):
        ImpactBotHarnessConfig(
            scanner_packages=("paigram_impact_bot",),
            telegram_runtime_objects=TelegramRuntimeObjects(),
        )
