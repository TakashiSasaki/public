# 3. Terminology

The key words `MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, and `MAY` are to be interpreted as normative requirements.

The following terms are used in this document.

`UUIDv8-FID-v2`
: The Format-ID UUIDv8 Profile Version 2 defined by this document.

`format_id`
: An 8-bit logical identifier composed of `format_type` and `format_subtype`.

`format_type`
: The upper 4 bits of `format_id`. This field identifies a broad payload family. This terminology section defines the field and its location. Concrete assignments are defined by the registry chapter and referenced format-specific documents.

`format_subtype`
: The lower 4 bits of `format_id`. This field identifies a concrete payload layout within a `format_type` family. This terminology section defines the field and its location. Concrete assignments are defined by the registry chapter and referenced format-specific documents.

`format_id_hi4`
: The physical 4-bit field fragment occupying bits 52 through 55. Semantically, this field is `format_type`.

`format_id_lo4`
: The physical 4-bit field fragment occupying bits 68 through 71. Semantically, this field is `format_subtype`.

`part3_control_octet`
: The octet containing the UUID version field and `format_id_hi4`.

`part3_reserved_octet`
: The low-order octet of Part 3. This octet is reserved for future definition.

`part4_control_octet`
: The octet containing the UUID variant field, `part4_reserved_bits`, and `format_id_lo4`.

`part4_reserved_bits`
: The two bits occupying bits 66 through 67. These bits are reserved and are set to zero in UUIDv8-FID-v2.

`part4_reserved_octet`
: The low-order octet of Part 4. This octet is reserved for future definition.

`Part 1` through `Part 5`
: The five hexadecimal groups in the canonical UUID string representation:

```text
xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Part1    Part2 Part3 Part4 Part5
```
