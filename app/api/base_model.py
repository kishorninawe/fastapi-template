from typing import Any, ClassVar, LiteralString

from pydantic import BaseModel as PydanticBaseModel, ValidationError
from pydantic_core import InitErrorDetails, PydanticCustomError


class BaseModel(PydanticBaseModel):
    error_messages: ClassVar[dict[str, dict[str, LiteralString]]] = {}

    def __init__(self, /, **data: Any) -> None:
        try:
            super().__init__(**data)
        except ValidationError as e:
            new_errors: list[InitErrorDetails] = []
            for error in e.errors():
                custom_message = self.error_messages.get(error["loc"][0], {}).get(error["type"])
                ctx = error.get("ctx")
                if custom_message:
                    new_errors.append(
                        InitErrorDetails(
                            type=PydanticCustomError(
                                error["type"],
                                custom_message.format(**ctx) if ctx else custom_message,
                            ),
                            loc=error["loc"],
                            input=error.get("input"),
                            ctx=ctx,
                        )
                    )
                else:
                    new_errors.append(
                        InitErrorDetails(
                            type=PydanticCustomError(
                                error["type"],
                                error.get("msg"),
                            ),
                            loc=error["loc"],
                            input=error.get("input"),
                            ctx=ctx,
                        )
                    )

            raise ValidationError.from_exception_data(title=self.__class__.__name__, line_errors=new_errors)
