from pydantic import ConfigDict, EmailStr, Field, field_validator

from app.api.base_model import BaseModel
from app.common.enums import GenderEnum
from app.utils.helpers import get_enum_values


class UserSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, strict=True)

    email: EmailStr = Field(
        title="Mobile number of the user", examples=["johndoe@gmail.com"]
    )
    password: str = Field(
        title="Mobile number of the user", examples=["12345"]
    )

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, v: str) -> str:
        return v.lower()


class UserRegisterSchema(UserSchema):
    gender: str = Field(
        title="Mobile number of the user",
        examples=[GenderEnum.MALE],
        enum=get_enum_values(GenderEnum)
    )
