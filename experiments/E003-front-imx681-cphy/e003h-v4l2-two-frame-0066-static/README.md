# E003h 0066 — bounded two-frame V4L2 proof

0066 extends the proven 0065 ordinary V4L2 bridge from one returned frame to two returned frames in one STREAMON session. It adds no hardware programming: slot1 BUS retarget and replay2 already exist in 0065. The delta waits for the second CSID VIDEO generation, retires the already-queued slot1, returns both vb2 buffers, then uses the same proven teardown.

Runtime remains unarmed until a separately hashed Golden-safe candidate package is inspected and authorized.
