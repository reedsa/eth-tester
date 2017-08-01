from __future__ import unicode_literals

from eth_utils import (
    is_canonical_address,
    is_list_like,
)

from eth_tester.constants import (
    UINT2048_MAX,
)
from eth_tester.exceptions import (
    ValidationError,
)

from .base import BaseOutputValidationBackend
from .common import (
    if_not_null,
    validate_bytes,
    validate_positive_integer,
    validate_dict,
    validate_no_extra_keys,
    validate_has_required_keys,
)


def validate_32_byte_string(value):
    validate_bytes(value)
    if len(value) != 32:
        raise ValidationError(
            "Must be of length 32.  Got: {0} of length {1}".format(value, len(value))
        )


validate_block_hash = validate_32_byte_string


def validate_nonce(value):
    validate_bytes(value)
    if len(value) != 8:
        raise ValidationError(
            "Must be of length 8.  Got: {0} of lenght {1}".format(value, len(value))
        )


def validate_logs_bloom(value):
    validate_positive_integer(value)
    if value > UINT2048_MAX:
        raise ValidationError("Value exceeds 2048 bit integer size: {0}".format(value))


def validate_canonical_address(value):
    validate_bytes(value)
    if not is_canonical_address(value):
        raise ValidationError("Value must be a 20 byte string")


BLOCK_VALIDATORS = {
    "number": validate_positive_integer,
    "hash": validate_block_hash,
    "parent_hash": validate_block_hash,
    "nonce": validate_nonce,
    "sha3_uncles": validate_32_byte_string,
    "logs_bloom": validate_logs_bloom,
    "transactions_root": validate_32_byte_string,
    "state_root": validate_32_byte_string,
    "miner": validate_canonical_address,
    "difficulty": validate_positive_integer,
    "total_difficulty": validate_positive_integer,
    "size": validate_positive_integer,
    "extra_data": validate_32_byte_string,
    "gas_limit": validate_positive_integer,
    "gas_used": validate_positive_integer,
    "timestamp": validate_positive_integer,
    "transactions": "TODO",
    "uncles": "TODO",
}


def validate_block(value):
    validate_dict(value)

    validate_no_extra_keys(value, set(BLOCK_VALIDATORS.keys()))
    validate_has_required_keys(value, set(BLOCK_VALIDATORS.keys()))

    for key, validator_fn in BLOCK_VALIDATORS.items():
        item = value[key]
        validator_fn(item)


def validate_log_entry_type(value):
    if value not in {"pending", "mined"}:
        raise ValidationError("Log entry type must be one of 'pending' or 'mined'")


def validate_log_entry_topics(value):
    if not is_list_like(value):
        raise ValidationError("Log entry topics must be a sequence")
    for item in value:
        validate_32_byte_string(item)


LOG_ENTRY_VALIDATORS = {
    "type": validate_log_entry_type,
    "log_index": validate_positive_integer,
    "transaction_index": if_not_null(validate_positive_integer),
    "transaction_hash": validate_32_byte_string,
    "block_hash": if_not_null(validate_32_byte_string),
    "block_number": if_not_null(validate_positive_integer),
    "address": validate_canonical_address,
    "data": validate_bytes,
    "topics": validate_log_entry_topics,
}


def validate_log_entry(value):
    validate_dict(value)
    validate_no_extra_keys(value, LOG_ENTRY_VALIDATORS.keys())
    validate_has_required_keys(value, LOG_ENTRY_VALIDATORS.keys())

    for key, validator_fn in LOG_ENTRY_VALIDATORS.items():
        item = value[key]
        validator_fn(item)


class OutputValidationBackend(BaseOutputValidationBackend):
    validate_block_hash = staticmethod(validate_block_hash)
    validate_block = staticmethod(validate_block)
    validate_log_entry = staticmethod(validate_log_entry)
