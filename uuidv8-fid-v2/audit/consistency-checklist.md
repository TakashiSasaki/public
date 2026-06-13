# UUIDv8-FID-v2 Consistency Checklist

This checklist records current invariants. Reviewers should check these items to verify consistency when proposing changes.

## 1. Registry invariants

- [ ] `0x10` remains the only assigned concrete Format ID.
- [ ] `0x11..0xef` remains unassigned.
- [ ] `0x00..0x0f` remains reserved.
- [ ] `0xf0..0xff` remains reserved.
- [ ] `0x7a` remains unassigned and is used only as an extraction/conformance example.
- [ ] No new Format ID is assigned unless `20-registry.md` and a referenced format-specific document are updated together.

## 2. Bit-layout invariants

- [ ] `version = 1000` occupies bits 48..51.
- [ ] `format_id_hi4 = format_type` occupies bits 52..55.
- [ ] `part3_reserved_octet` occupies bits 56..63.
- [ ] `variant = 10` occupies bits 64..65.
- [ ] `part4_reserved_bits = 00` occupies bits 66..67.
- [ ] `format_id_lo4 = format_subtype` occupies bits 68..71.
- [ ] `part4_reserved_octet` occupies bits 72..79.
- [ ] `format_id = (format_type << 4) | format_subtype`.

## 3. Document-role invariants

- [ ] Top-level files remain non-normative entry-point stubs.
- [ ] Canonical specification sections remain under `uuidv8-fid-v2/`.
- [ ] Concrete format specifications remain under `formats/`.
- [ ] Conformance material remains derived and non-normative.
- [ ] Implementation guidance remains derived and non-normative.
- [ ] Audit material remains derived and non-normative.

## 4. time48-rand invariants

- [ ] `format_type = 0x1`.
- [ ] `format_subtype = 0x0`.
- [ ] `format_id = 0x10`.
- [ ] center form remains `8100-8000`.
- [ ] Part 5 remains `unix_ts_ms`, a 48-bit unsigned Unix epoch millisecond timestamp encoded in network byte order.
- [ ] Part 1 and Part 2 remain `rand_a` and `rand_b`, 48 total payload bits outside control and timestamp fields.
- [ ] Existing deterministic vectors remain unchanged.

## 5. Conformance-vector invariants

- [ ] Markdown and JSON conformance vectors both contain cases A through I.
- [ ] Case A remains assigned `0x10`.
- [ ] Case B remains unassigned `0x7a` and does not assign it.
- [ ] Cases C and D remain reserved Format ID examples.
- [ ] Cases E, F, and G remain invalid structural/control-field examples.
- [ ] Cases H and I remain assigned `0x10` with nonzero reserved octets, structural pass, strict fail, generation no.
- [ ] `generation_allowed_by_this_version` is true only for Case A.

## 6. Implementation-guidance invariants

- [ ] Pseudocode does not redefine the specification.
- [ ] `parse_time48_rand` performs UUIDv8-FID-v2 structural validation before accepting the format.
- [ ] `construct_uuidv8_fid_v2` rejects reserved and unassigned Format IDs for interoperable use.
- [ ] `construct_uuidv8_fid_v2` rejects unknown Format IDs.
- [ ] Deprecated Format IDs are not generated unless explicitly accepted for compatibility.
- [ ] Validation pseudocode preserves the distinction between basic, structural, profile, and strict validation.
