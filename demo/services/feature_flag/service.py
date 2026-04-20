from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import scoped_session

from ...lib.exceptions import DuplicateFeatureFlagError, FeatureFlagNotFoundError
from ...models import FeatureFlag


class FeatureFlagService:
    ALLOWED_UPDATE_FIELDS = {"name", "description", "enabled", "environment"}

    def __init__(self, session):
        self.session: scoped_session = session

    # Public API

    def create_flag(
        self,
        name: str,
        enabled: bool = False,
        environment: str = "dev",
        description: str | None = None,
    ) -> FeatureFlag:

        flag = FeatureFlag(
            name=name,
            enabled=enabled,
            environment=environment,
            description=description,
        )

        self.session.add(flag)

        try:
            self._commit()
        except IntegrityError:
            raise DuplicateFeatureFlagError(name=name)

        return flag

    def get_flag(self, flag_id: int) -> FeatureFlag:
        return self._get_or_raise(flag_id)

    def update_flag(self, flag_id: int, data: dict) -> FeatureFlag:
        flag = self._get_or_raise(flag_id)

        # filter data for allowed items
        updates = {}
        for key, value in data.items():
            if key in self.ALLOWED_UPDATE_FIELDS:
                updates[key] = value

        # update the values
        for key, value in updates.items():
            setattr(flag, key, value)

        try:
            self._commit()
        except IntegrityError:
            raise DuplicateFeatureFlagError(name=flag.name)

        return flag

    def toggle_flag(self, flag_id: int) -> FeatureFlag:
        flag = self._get_or_raise(flag_id)

        flag.toggle()

        self._commit()

        return flag

    def list_flags(self, environment: str | None = None):
        stmt = select(FeatureFlag)

        if environment:
            stmt = stmt.where(FeatureFlag.environment == environment)

        stmt = stmt.order_by(FeatureFlag.name)

        return self.session.execute(stmt).scalars().all()

    def list_public_flags(self):
        stmt = select(FeatureFlag).where(FeatureFlag.enabled.is_(True)).order_by(FeatureFlag.name)

        result = self.session.execute(stmt)

        return result.scalars().all()

    def delete_flag(self, flag_id: int) -> None:
        flag = self.get_flag(flag_id)

        self.session.delete(flag)
        self._commit()

    # Internal Helpers

    def _get_or_raise(self, flag_id: int) -> FeatureFlag:
        flag = self.session.get(FeatureFlag, flag_id)

        if flag is None:
            raise FeatureFlagNotFoundError(flag_id=flag_id)

        return flag

    def _commit(self) -> None:
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
