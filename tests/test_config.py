from pathlib import Path

from task_evidence_mcp.config import AppConfig, load_config


def test_to_toml_contains_expected_sections() -> None:
    config = AppConfig()
    text = config.to_toml()

    assert "[storage]" in text
    assert "[capture]" in text
    assert 'artifacts_dir = "artifacts"' in text
    assert 'screenshot_format = "png"' in text
    assert 'recording_format = "mp4"' in text
    assert "recording_frame_rate = 8" in text
    assert 'macos_avfoundation_input = "Capture screen 0:none"' in text
    assert "macos_capture_cursor = true" in text
    assert 'linux_x11_display = ":0.0"' in text
    assert "linux_draw_mouse = true" in text
    assert "[ocr]" in text
    assert 'backend = "tesseract"' in text


def test_resolve_artifacts_dir_is_based_on_given_directory() -> None:
    config = AppConfig(artifacts_dir="evidence")
    resolved = config.resolve_artifacts_dir(Path("D:/workspace"))

    assert resolved.as_posix().endswith("/workspace/evidence")


def test_load_config_reads_toml_values(tmp_path: Path) -> None:
    config_path = tmp_path / "task-evidence-mcp.toml"
    config_path.write_text(
        "\n".join(
            [
                "[storage]",
                'artifacts_dir = "evidence"',
                "",
                "[capture]",
                'screenshot_format = "bmp"',
                "recording_enabled = true",
                'macos_avfoundation_input = "Capture screen 1:none"',
                "macos_capture_cursor = false",
                'linux_x11_display = ":1.0"',
                "linux_draw_mouse = false",
                "",
            ]
        ),
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.artifacts_dir == "evidence"
    assert config.screenshot_format == "bmp"
    assert config.recording_enabled is True
    assert config.recording_format == "mp4"
    assert config.recording_frame_rate == 8
    assert config.macos_avfoundation_input == "Capture screen 1:none"
    assert config.macos_capture_cursor is False
    assert config.linux_x11_display == ":1.0"
    assert config.linux_draw_mouse is False
    assert config.ocr_enabled is False
