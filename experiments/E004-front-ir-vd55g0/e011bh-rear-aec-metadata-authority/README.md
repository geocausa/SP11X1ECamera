# E011BH: original metadata, name and comparison helpers

Original module metadata constructor0x6F45D8, name helper0x6F4AC0 and comparison0xF5DF00 now execute in isolated owned fixtures. Their skips are removed only from metadata-fixture-private.py, an isolated copy of the owned E011BE initializer. Historical full-parent fixtures remain unchanged and still skip these helpers. Original bytes stay on SP11.

## Verified helper behavior

The seven constructor arguments are explicitly owned: object, primary name, three numeric fields, profile string and filename string. The original constructor returns its object and installs base vtable0x133B770. One allocation holds the complete primary name and its terminator, with pointer at object+8. The embedded40-byte name-helper output at+16 equals a separate original helper invocation; ASCII names through32 characters preserve their case and text. The opaque tail algorithm is not independently derived.

Argument x2 is written at+60, x3 at+68 and x4 at+72. Zero fields at+56/+64/+76 and+280:288 are checked. Numeric bit patterns include0/U32max; these are forwarding tests, not accepted selector/mode policy.

Profile text is stored at+80 with a127-character limit, filename text at+208 with a64-character limit. Original copy-helper calls6F46AC/6F46C0/6F46D8 execute. Overlength owned strings confirm truncation at those limits. All heap bytes outside the qualified fields and name allocation remain unchanged; source strings and allocation redzones are intact.

Original comparison is case-sensitive, null-terminated and yields the expected lexical sign for the owned pairs. It preserves the complete heap. Changing the stale third argument0/1/384/U64max does not alter these bounded results; no comparison helper is skipped.

## Validation

- 44 original metadata constructor returns:11 owned cases at four placements0/1/0x1230/0x8010.
- 44 separate name-helper returns plus44 original calls embedded in the constructor.
- 192 original comparison cases:12 pairs, four placements, four third-argument values.
- 15 fixture-scope rejections before execution, with heap unchanged.
- Names0..32 ASCII, profile inputs0..160 and filename inputs0..96; profile/file boundary and truncation cases included.

Allocation/memset and security-cookie helpers11D0/11F0/CAE740/F5E600 are the only remaining isolated fixture skips. There are no original OEM bytes in the committed source or evidence.

## Parent authority still open

Original caller anchors qualify profile pointer reader+72 at123D5C, minor reader+68 at123D68, reader->file context at123D58 and filename context+0 at123D74. The original compiled AEC name matches the typed source name. These reads do not prove how the loader populates them.

The old full-parent fixture left those metadata fields absent. The initial four-argument isolated call reached native invalid-parameter handling because its profile/filename pointers were missing; the corrected seven-argument owned call returned. This is a fixture completeness issue, not a driver-defect claim. An initial expected filename capacity was corrected from71 characters to the original64-character copy limit. A zero field+76 was added to exact write checks. Names beyond32 exhibit a different encoding and are excluded; no simple prefix truncation is claimed for them.

Owned labels such as Default and owned-fixture.bin are explicit fixture inputs. They are not proof of actual selected profile or opened filename. Before removing the skips from the full parent, trace the loader's source/selector/header ownership for reader metadata and filename pointer, and account for the constructor's new name allocation. Remaining root/grid scalar coverage, full aggregate/profile authority and all runtime ownership gates remain open.

Run only on the original SP11:

```sh
python3 experiments/E004-front-ir-vd55g0/e011bh-rear-aec-metadata-authority/source-private.py
```

No camera start, reboot, observer, production C or kernel build. Golden boot50edbeb8-e42d-41b1-8b37-3d536443604f/all three hashes unchanged, saved FullIOv19c/empty next_entry, NTFS unmounted/camera idle. Native rear runtime remains DENIED. E011BD Windows identity remains consumed/initialization incomplete.

See METADATA-SAFE.json, GUARD-SAFE.json, RESULT.json and NEXT-SOURCE.json.
