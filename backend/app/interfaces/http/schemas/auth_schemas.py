from marshmallow import EXCLUDE, RAISE, Schema, ValidationError, fields, validate, validates_schema

from app.domain.entities.enums import OtpPurpose


class StrictSchema(Schema):
    class Meta:
        unknown = RAISE


class RegisterSchema(StrictSchema):
    first_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    last_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(load_default=None, allow_none=True)
    phone = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=32))
    password = fields.String(required=True, load_only=True, validate=validate.Length(max=256))
    preferred_locale = fields.String(
        load_default="fa", validate=validate.OneOf(["fa", "en"])
    )

    @validates_schema
    def validate_contact(self, data, **kwargs):
        if not data.get("email") and not data.get("phone"):
            raise ValidationError("Provide an email address or phone number.", "_schema")


class LoginSchema(StrictSchema):
    identifier = fields.String(required=True, validate=validate.Length(min=3, max=320))
    password = fields.String(required=True, load_only=True, validate=validate.Length(max=256))


class OtpRequestSchema(StrictSchema):
    destination = fields.String(required=True, validate=validate.Length(min=3, max=320))
    purpose = fields.String(
        required=True, validate=validate.OneOf([purpose.value for purpose in OtpPurpose])
    )


class OtpVerifySchema(OtpRequestSchema):
    code = fields.String(
        required=True,
        validate=(validate.Length(min=4, max=10), validate.Regexp(r"^\d+$")),
    )


class ChangePasswordSchema(StrictSchema):
    current_password = fields.String(required=True, load_only=True, validate=validate.Length(max=256))
    new_password = fields.String(required=True, load_only=True, validate=validate.Length(max=256))
