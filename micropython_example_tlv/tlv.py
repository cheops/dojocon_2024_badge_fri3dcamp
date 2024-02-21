
try:
    from collections.abc import Callable
except ImportError:
    pass

import struct


class TLVException(Exception):
    """Type-Length-Value Exception"""


class TLVParseException(TLVException):
    """Type-Length-Value Parse Exception"""


class TLVUnknownTypeException(TLVException):
    """Type-Length-Value Unknown Type Exception"""


class TLVMalformedException(TLVException):
    """Type-Length-Value Malformed Exception"""


class TLVParser:
    """
    TLV Parser: can encode and decode Type-Length_Value bytes
    use the add_tlv_mapping function to define your callbacks for each tlv
    """
    _TYPE_LENGTH_FMT = '<BB'
    _FMT_LENGTH = struct.calcsize(_TYPE_LENGTH_FMT)

    def __init__(self):
        self._apply_mapping: dict[int, [int, Callable[[bytes], None]]] = {}

    @staticmethod
    def decode(in_bytes: bytes) -> list[tuple[int, int, bytes]]:
        decoded = []
        offset = 0
        while len(in_bytes) - offset >= TLVParser._FMT_LENGTH:
            tlv_type, tlv_length = struct.unpack_from(TLVParser._TYPE_LENGTH_FMT, in_bytes, offset)

            if tlv_length > 0 and len(in_bytes) - offset >= TLVParser._FMT_LENGTH + tlv_length:
                tlv_value = in_bytes[offset + 2:offset + TLVParser._FMT_LENGTH + tlv_length]
            else:
                tlv_value = bytes()

            decoded.append((tlv_type, tlv_length, tlv_value))

            offset = offset + TLVParser._FMT_LENGTH + tlv_length

        if len(in_bytes) - offset != 0:
            raise TLVParseException(f"remaining bytes cannot be decoded: {in_bytes[offset:]}")

        return decoded

    @staticmethod
    def encode(tlv_type: int, tlv_value: bytes) -> bytes:
        encoded = bytearray()
        encoded.append(tlv_type)
        encoded.append(len(tlv_value))
        encoded.extend(tlv_value)
        return bytes(encoded)

    @staticmethod
    def _check_tlv_length(expected_value_length: int, tlv_length: int, tlv_type: int) -> None:
        if expected_value_length is not None and tlv_length != expected_value_length:
            raise TLVMalformedException(f"{tlv_type=} {expected_value_length=} but got: {tlv_length=}")

    def add_tlv_mapping(self, tlv_type: int, expected_value_length: int, callback: Callable[[bytes], None]) -> None:
        """add a callback for tlv_type"""
        self._apply_mapping[tlv_type] = (expected_value_length, callback)

    def apply_tlv(self, tlv_type: int, tlv_length: int, tlv_value: bytes, skip_unknown: bool = True) -> None:
        print(f"applying {tlv_type=} {tlv_length=} {tlv_value=}")

        if not skip_unknown and tlv_type not in self._apply_mapping:
            raise TLVUnknownTypeException(f"{tlv_type=} not known {tlv_length=} {tlv_value=}")

        if tlv_type in self._apply_mapping:
            expected_length, mapping_callback = self._apply_mapping[tlv_type]
            TLVParser._check_tlv_length(expected_length, tlv_length, tlv_type)
            mapping_callback(tlv_value)

    def apply_tlvs(self, decoded: list[tuple[int, int, bytes]], skip_unknown: bool = True):
        for d in decoded:
            self.apply_tlv(*d, skip_unknown)


if __name__ == "__main__":
    print("this is a module, running it does nothing")
