from migrator.core.detector import ModelDetector


def test_find_base_returns_none_when_not_found(temp_dir):
    """Test that find_base returns None when no Base found"""
    result = ModelDetector.find_base()
    assert result is None


def test_scan_project_skips_excluded_dirs(temp_dir):
    """Test that scan skips venv and other excluded directories"""
    venv_dir = temp_dir / "venv"
    venv_dir.mkdir()

    model_file = venv_dir / "models.py"
    model_file.write_text("class Base: pass")

    result = ModelDetector.find_base()
    assert result is None
