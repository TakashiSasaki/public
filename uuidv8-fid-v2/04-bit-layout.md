# 5. Bit Numbering

This document numbers bits from 0 to 127, in network byte order, from the most significant bit of the UUID to the least significant bit of the UUID.

Octets are numbered from 0 to 15.

```text
Octet 0  contains bits   0..7
Octet 1  contains bits   8..15
...
Octet 15 contains bits 120..127
```

The canonical UUID parts correspond to octets as follows:

```text
Part1: octets  0..3
Part2: octets  4..5
Part3: octets  6..7
Part4: octets  8..9
Part5: octets 10..15
```

# 6. Overall Layout

UUIDv8-FID-v2 has the following bit layout:

```text
bits    field

0..31   part1
32..47  part2

48..51  version = 1000
52..55  format_id_hi4 = format_type
56..63  part3_reserved_octet

64..65  variant = 10
66..67  part4_reserved_bits = 00
68..71  format_id_lo4 = format_subtype
72..79  part4_reserved_octet

80..127 part5
```

The logical Format ID is computed as:

```text
format_id = (format_type << 4) | format_subtype
```

Equivalently:

```text
format_id = (format_id_hi4 << 4) | format_id_lo4
```

The valid numeric range of `format_id` is:

```text
0x00..0xff
```

or equivalently:

```text
0..255
```
