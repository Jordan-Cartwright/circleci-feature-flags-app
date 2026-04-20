import pytest

from demo.config.settings import ApplicationSettings


@pytest.mark.parametrize(
    "name,value,expected",
    [("db_name", 123, "123")],
)
def test_convert_type_str(name, value, expected):
    result = ApplicationSettings.convert_type(name, value)
    assert result == expected


def test_convert_type_unknown_key_returns_value():
    result = ApplicationSettings.convert_type("unknown_key", 123)
    assert result == 123


@pytest.mark.parametrize(
    "value,expected",
    [
        ("true", True),
        ("True", True),
        ("yes", True),
        ("1", True),
        ("false", False),
        ("0", False),
    ],
)
def test_convert_type_bool(value, expected):
    ApplicationSettings.types["feature_enabled"] = bool

    result = ApplicationSettings.convert_type("feature_enabled", value)

    assert result is expected


@pytest.mark.parametrize(
    "env_var, value, use_file",
    [
        ("DB_HOST", "10.0.0.5", False),
        ("DB_HOST", "192.168.1.50", True),
    ],
)
def test_load_environment_sets_value(app, monkeypatch, tmp_path, env_var, value, use_file):
    if use_file:
        file_path = tmp_path / "value.txt"
        file_path.write_text(value)
        monkeypatch.setenv(f"{env_var}_FILE", str(file_path))
    else:
        monkeypatch.setenv(env_var, value)

    ApplicationSettings.load_environment(app)

    assert app.config[env_var] == value


@pytest.mark.parametrize(
    "env_var,input_value,expected_value",
    [
        ("DB_NAME", "123", "123"),
        ("DB_PORT", "5433", 5433),
    ],
)
def test_type_conversion_applied(app, monkeypatch, env_var, input_value, expected_value):
    monkeypatch.setenv(env_var, input_value)

    ApplicationSettings.load_environment(app)

    assert app.config[env_var] == expected_value
    assert isinstance(
        app.config[env_var],
        ApplicationSettings.types[env_var.lower()],
    )


@pytest.mark.parametrize("env_var", ["DB_HOST", "DB_PORT", "DB_USER"])
def test_missing_env_does_not_modify_config(app, monkeypatch, env_var):
    monkeypatch.setattr("os.environ", {})

    original_config = dict(app.config)

    ApplicationSettings.load_environment(app)

    assert dict(app.config) == original_config


def test_raises_if_both_env_and_file_set(app, monkeypatch, tmp_path):
    file_path = tmp_path / "value.txt"
    file_path.write_text("192.168.1.50")

    monkeypatch.setenv("DB_HOST", "10.0.0.5")
    monkeypatch.setenv("DB_HOST_FILE", str(file_path))

    with pytest.raises(AttributeError):
        ApplicationSettings.load_environment(app)
