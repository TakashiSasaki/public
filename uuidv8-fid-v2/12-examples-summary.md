# 18. Example: Extracting the Format ID

Suppose a UUID has the following relevant octets:

```text
octet6 = 0x87
octet8 = 0x8a
```

Then:

```text
version             = 0x8
format_id_hi4       = 0x7
format_type         = 0x7

variant             = 0b10
part4_reserved_bits = 0b00
format_id_lo4       = 0x0a
format_subtype      = 0x0a
```

Therefore:

```text
format_id = (0x7 << 4) | 0x0a
          = 0x7a
```

The UUID is structurally a UUIDv8-FID-v2 value with `format_type = 0x7`, `format_subtype = 0x0a`, and `format_id = 0x7a`, assuming the complete UUID is otherwise syntactically valid.

A structurally valid UUIDv8-FID-v2 value carrying this unassigned Format ID would have the following center form:

```text
xxxxxxxx-xxxx-8700-8a00-xxxxxxxxxxxx
```

This example demonstrates extraction and structural layout only; it does not assign `format_id = 0x7a`.

The first assigned UUIDv8-FID-v2 payload format is `format_id = 0x10`, defined in `formats/10-time48-rand.md`.

# 19. Summary

UUIDv8-FID-v2 is a UUID version 8 profile that introduces an 8-bit logical Format ID.

The Format ID is composed of two semantic nibbles:

```text
format_type:    bits 52..55
format_subtype: bits 68..71
```

The same physical fields are named:

```text
format_id_hi4: bits 52..55
format_id_lo4: bits 68..71
```

The profile also defines reserved fields:

```text
part4_reserved_bits:  bits 66..67
part3_reserved_octet: bits 56..63
part4_reserved_octet: bits 72..79
```

The core layout is:

```text
bits  48..51   version = 1000
bits  52..55   format_id_hi4 = format_type
bits  56..63   part3_reserved_octet

bits  64..65   variant = 10
bits  66..67   part4_reserved_bits = 00
bits  68..71   format_id_lo4 = format_subtype
bits  72..79   part4_reserved_octet
```

The logical Format ID is reconstructed as:

```text
format_id = (format_type << 4) | format_subtype
```

Generated UUIDv8-FID-v2 values have the following center form:

```text
xxxxxxxx-xxxx-8T00-8S00-xxxxxxxxxxxx
```
