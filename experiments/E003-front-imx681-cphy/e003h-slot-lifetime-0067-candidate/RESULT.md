# E003h 0067 result — five-group slot lifetime validated

0067 repeated the successful ordinary two-frame V4L2 session with no hardware-programming change. Both 7,778,304-byte QC10C frames completed and are distinct. The new software-only lifetime accounting required Windows-proven CSID BUF_DONE groups VIDEO, AEC/BHIST, TINTLESS, AWB and RS to retire for each slot; the 0067 success path proves both slot0 and slot1 reached reusable state before teardown. RT-CDM stopped fault-free at FIFO 30 and the machine returned cleanly to Golden.

No slot was actually reused and no third frame was attempted. The next gate is a separately authorized frame-3 slot-reuse proof using only exact captured replay/request evidence.
