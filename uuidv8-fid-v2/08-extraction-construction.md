# 12. Extraction Formulas

For implementations using octet-oriented access, the following formulas define extraction.

Let:

```text
octet6 = UUID octet 6
octet7 = UUID octet 7
octet8 = UUID octet 8
octet9 = UUID octet 9
```

Then:

```text
part3_control_octet   = octet6
part3_reserved_octet  = octet7
part4_control_octet   = octet8
part4_reserved_octet  = octet9

version               = (octet6 >> 4) & 0x0f
format_id_hi4         =  octet6       & 0x0f
format_type           =  format_id_hi4

variant               = (octet8 >> 6) & 0x03
part4_reserved_bits   = (octet8 >> 4) & 0x03
format_id_lo4         =  octet8       & 0x0f
format_subtype        =  format_id_lo4

format_id             = (format_type << 4) | format_subtype
```

For UUIDv8-FID-v2:

```text
version MUST be 0x8
variant MUST be 0b10
part4_reserved_bits MUST be 0b00
```

# 13. Construction Formulas

Given `format_type` and `format_subtype`, the control octets are constructed as follows:

```text
format_id_hi4 = format_type    & 0x0f
format_id_lo4 = format_subtype & 0x0f

part3_control_octet = 0x80 | format_id_hi4
part4_control_octet = 0x80 | format_id_lo4
```

The reserved fields are set as follows:

```text
part4_reserved_bits   = 0b00
part3_reserved_octet  = 0x00
part4_reserved_octet  = 0x00
```

The expression `0x80 | format_id_lo4` sets the two most significant bits of `part4_control_octet` to `10`, sets bits 66 through 67 to `00`, and stores `format_id_lo4` in the low-order nibble.
