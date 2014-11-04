from __future__ import unicode_literals

import binascii

from django.conf import settings
from django.core import exceptions
from django.db import models
from django.db.models import fields
from django.utils import six

from .compat import force_bytes, force_text

try:
    import Crypto.Cipher.AES
except ImportError: # pragma: no cover
    raise ImportError('PyCrypto is required to use django-all-access.')


class EncryptedField(six.with_metaclass(models.SubfieldBase, models.TextField)):
    """
    This code is based on http://www.djangosnippets.org/snippets/1095/
    and django-fields https://github.com/svetlyak40wt/django-fields
    """

    cipher_class = Crypto.Cipher.AES
    prefix = b'$AES$'

    def __init__(self, *args, **kwargs):
        self.cipher = self.cipher_class.new(force_bytes(settings.SECRET_KEY)[:32])
        super(EncryptedField, self).__init__(*args, **kwargs)

    def _is_encrypted(self, value):

        return value.startswith(self.prefix)

    def _get_padding(self, value):
        # We always want at least 2 chars of padding (including zero byte),
        # so we could have up to block_size + 1 chars.
        mod = (len(value) + 2) % self.cipher.block_size
        return self.cipher.block_size - mod + 2

    def to_python(self, value):
        if value is None:
            return value
        value = force_bytes(value)
        if self._is_encrypted(value):
            hexdigest = value[len(self.prefix):]
            encrypted = binascii.a2b_hex(hexdigest)
            decrypted = self.cipher.decrypt(encrypted).split(b'\x00')[0]
            return force_text(decrypted)
        return force_text(value)

    def get_db_prep_value(self, value, connection=None, prepared=False):
        if self.null:
            # Normalize empty values to None
            value = value or None
        if value is None:
            return None
        value = force_bytes(value)
        if not self._is_encrypted(value):
            padding  = self._get_padding(value)
            if padding > 0:
                value = value + b'\x00' + b'*' * (padding - 1)
            value = self.prefix + binascii.b2a_hex(self.cipher.encrypt(value))
        return force_text(value)


# pragma: no cover
try:
    from south.modelsinspector import add_introspection_rules
except ImportError: # pragma: no cover
    # South not installed
    pass
else:
    add_introspection_rules([], ["^allaccess\.fields\.EncryptedField"])


class BigAutoField(fields.AutoField):
    """ Bigint auto increment field """
    def db_type(self, connection):
        if settings.DATABASE_ENGINE == 'mysql':
            return "bigint AUTO_INCREMENT"
        elif settings.DATABASE_ENGINE == 'oracle':
            return "NUMBER(19)"
        elif settings.DATABASE_ENGINE[:8] == 'postgres':
            return "bigserial"
        else:
            raise NotImplemented

    def get_internal_type(self):
        return "BigAutoField"

    def to_python(self, value):
        if value is None:
            return value
        try:
            return int(value)
        except (TypeError, ValueError):
            raise exceptions.ValidationError(
                ("This value must be a long integer.")
            )


class BigForeignKey(fields.related.ForeignKey):
    """ Foreign Key for bigint field """
    def db_type(self, connection):
        rel_field = self.rel.get_related_field()
        # next lines are the "bad tooth" in the original code:
        if (isinstance(rel_field, BigAutoField) or
           (isinstance(rel_field, BigUUIDField)) or
            (not connection.features.related_fields_match_type and
                isinstance(rel_field, fields.BigIntegerField))):
            # because it continues here in the django code:
            # return IntegerField().db_type()
            # thereby fixing any AutoField as IntegerField
            return fields.BigIntegerField().db_type(connection)
        return rel_field.db_type(connection)


class BigUUIDField(fields.AutoField):
    """ UUID auto created using bigint """
    def db_type(self, connection):
        return 'bigint DEFAULT id_generator()'

    def get_internal_type(self):
        return "BigUUIDField"

    def to_python(self, value):
        if value is None:
            return value
        try:
            return int(value)
        except (TypeError, ValueError):
            raise exceptions.ValidationError(
                ("This value must be a long integer.")
            )
