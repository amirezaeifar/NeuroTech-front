from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.entities.base import BIGINT, Base, IdMixin, PublicIdMixin, SoftDeleteMixin, TimestampMixin


class MediaAsset(IdMixin, PublicIdMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "media_assets"

    uploaded_by: Mapped[int | None] = mapped_column(BIGINT, ForeignKey("users.id", ondelete="SET NULL"), index=True)
    file_name: Mapped[str] = mapped_column(String(500))
    original_name: Mapped[str] = mapped_column(String(500))
    mime_type: Mapped[str] = mapped_column(String(255), index=True)
    file_size: Mapped[int] = mapped_column(BIGINT)
    storage_path: Mapped[str] = mapped_column(String(2048))
    public_url: Mapped[str | None] = mapped_column(String(2048))
    checksum: Mapped[str] = mapped_column(String(128), index=True)
