from enum import Enum

from sqlalchemy import Enum as SqlEnum


class ValueEnum(str, Enum):
    def __str__(self) -> str:
        return self.value


class UserStatus(ValueEnum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DISABLED = "disabled"


class RoleName(ValueEnum):
    ADMIN = "admin"
    SPECIALIST = "specialist"
    CONTENT_MANAGER = "content_manager"
    USER = "user"


class CourseTier(ValueEnum):
    FREE = "free"
    PREMIUM = "premium"


class CourseLevel(ValueEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class EnrollmentStatus(ValueEnum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class LessonProgressStatus(ValueEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class CommentStatus(ValueEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ProductStatus(ValueEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    DISCONTINUED = "discontinued"


class ReviewStatus(ValueEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class InquiryStatus(ValueEnum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class EventType(ValueEnum):
    ONLINE = "online"
    ONSITE = "onsite"
    HYBRID = "hybrid"


class EventStatus(ValueEnum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    LIVE = "live"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EventRegistrationStatus(ValueEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    WAITLISTED = "waitlisted"
    CANCELLED = "cancelled"


class AttendanceStatus(ValueEnum):
    UNKNOWN = "unknown"
    ATTENDED = "attended"
    ABSENT = "absent"


class PartnerType(ValueEnum):
    SPECIALIST = "specialist"
    INSTRUCTOR = "instructor"
    ORGANIZATION = "organization"
    AGENCY = "agency"


class PartnerStatus(ValueEnum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"


class TradeServiceType(ValueEnum):
    IMPORT = "import"
    EXPORT = "export"
    CONSULTING = "consulting"
    REGULATORY = "regulatory"


class TradeDocumentStatus(ValueEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class TradeGroupType(ValueEnum):
    TEXT = "text"
    LIST = "list"
    PAIRS = "pairs"


class OrderStatus(ValueEnum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class OrderItemType(ValueEnum):
    COURSE = "course"
    PRODUCT = "product"


class PaymentStatus(ValueEnum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"


class ContactMessageStatus(ValueEnum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class ContentType(ValueEnum):
    PAGE = "page"
    ARTICLE = "article"
    ANNOUNCEMENT = "announcement"
    FAQ = "faq"


class ContentStatus(ValueEnum):
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ModerationStatus(ValueEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"


class ModerationActionType(ValueEnum):
    APPROVE = "approve"
    REJECT = "reject"
    ESCALATE = "escalate"
    RESTORE = "restore"


class MediaType(ValueEnum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"


class OtpPurpose(ValueEnum):
    LOGIN = "login"
    REGISTRATION = "registration"
    PASSWORD_RESET = "password_reset"
    PHONE_VERIFICATION = "phone_verification"


def enum_type(enum_class: type[ValueEnum], length: int = 32) -> SqlEnum:
    return SqlEnum(
        enum_class,
        native_enum=False,
        validate_strings=True,
        values_callable=lambda members: [member.value for member in members],
        length=length,
    )
