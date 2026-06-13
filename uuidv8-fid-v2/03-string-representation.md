# 4. UUID String Representation

UUIDv8-FID-v2 uses the standard canonical UUID textual representation:

```text
xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

where each `x` is a lowercase or uppercase hexadecimal digit. Implementations SHOULD emit lowercase hexadecimal digits, but parsers MAY accept uppercase hexadecimal digits.

The five parts are:

```text
Part1: 32 bits,  8 hex digits
Part2: 16 bits,  4 hex digits
Part3: 16 bits,  4 hex digits
Part4: 16 bits,  4 hex digits
Part5: 48 bits, 12 hex digits
```

UUIDv8-FID-v2 does not change the canonical UUID string length, hyphen positions, or hexadecimal encoding.

In canonical UUID string form, the UUIDv8-FID-v2 control structure can be shown schematically as:

```text
xxxxxxxx-xxxx-8Trr-8Srr-xxxxxxxxxxxx
```

where:

```text
8   in Part 3 is the UUID version nibble for UUID version 8
T   in Part 3 is format_type, physically stored as format_id_hi4
rr  in Part 3 is part3_reserved_octet
8   in Part 4 is the hexadecimal digit produced by variant = 10 and part4_reserved_bits = 00
S   in Part 4 is format_subtype, physically stored as format_id_lo4
rr  in Part 4 is part4_reserved_octet
```

Generators conforming to this version of the specification set the reserved octets to zero. Generated UUIDv8-FID-v2 values therefore have the following center form:

```text
xxxxxxxx-xxxx-8T00-8S00-xxxxxxxxxxxx
```
