import pytest

from demo.lib.exceptions import DuplicateFeatureFlagError, FeatureFlagNotFoundError
from demo.services.feature_flag import FeatureFlagService


def test_create_flag(session):
    service = FeatureFlagService(session)

    flag = service.create_flag("test_flag")

    assert flag.id is not None
    assert flag.name == "test_flag"
    assert flag.enabled is False


def test_toggle_flag(session):
    service = FeatureFlagService(session)

    flag = service.create_flag("test_toggle_flag")

    assert flag.enabled is False

    flag.toggle()

    assert flag.enabled is True


def test_flag_primary_key_constraint(session):
    service = FeatureFlagService(session)

    flag1 = service.create_flag("test_constraint_flag")

    assert flag1.id is not None

    with pytest.raises(DuplicateFeatureFlagError) as err:
        # We should not be able to create feature flags with the same name within the same environment
        service.create_flag("test_constraint_flag")

    assert "already exists" in str(err.value)


def test_get_feature_flag_not_found(session):
    service = FeatureFlagService(session)

    with pytest.raises(FeatureFlagNotFoundError) as err:
        service.get_flag(999)

    assert "Feature flag '999' not found" in str(err.value)
