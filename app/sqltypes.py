import json

from sqlalchemy import (
    LargeBinary,
    TypeDecorator,
    func,
)

from app.core.config import settings


def encrypt(value):
    return func.pgp_sym_encrypt(value, settings.POSTGRES_ENCRYPTION_KEY)


def decrypt(value):
    return func.pgp_sym_decrypt(value, settings.POSTGRES_ENCRYPTION_KEY)


class EncryptedText(TypeDecorator):
    """ Custom type for encrypted text column """

    impl = LargeBinary
    cache_ok = True

    def bind_processor(self, dialect):
        # This will send value as it is, without converting in Binary
        if dialect.dbapi is None:
            return None

        def process(value):
            if value is not None:
                return value
            return None

        return process

    def bind_expression(self, bindvalue):
        # This will encrypt the data before sending it to the database
        return func.pgp_sym_encrypt(bindvalue, settings.POSTGRES_ENCRYPTION_KEY, type_=self)

    def column_expression(self, col):
        # This will decrypt the data when reading from the database
        return func.pgp_sym_decrypt(col, settings.POSTGRES_ENCRYPTION_KEY, type_=self)


class EncryptedJSON(TypeDecorator):
    """ Custom type for encrypted json columns """

    impl = LargeBinary
    cache_ok = True

    def bind_processor(self, dialect):
        if dialect.dbapi is None:
            return None

        def process(value):
            if value is not None:
                return json.dumps(value)
            return None

        return process

    def result_processor(self, dialect, coltype):
        if dialect.dbapi is None:
            return None

        def process(value):
            if value is not None:
                return json.loads(value)
            return None

        return process

    def bind_expression(self, bindvalue):
        # This will encrypt the data before sending it to the database
        return func.pgp_sym_encrypt(bindvalue, settings.POSTGRES_ENCRYPTION_KEY, type_=self)

    def column_expression(self, col):
        # This will decrypt the data when reading from the database
        return func.pgp_sym_decrypt(col, settings.POSTGRES_ENCRYPTION_KEY, type_=self)
