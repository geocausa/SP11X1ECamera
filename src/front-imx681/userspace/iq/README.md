# IQ producer authority snapshot

`live-iq-producer.py` is a byte-identical snapshot of the GM R5..R27 producer authority. It is **not yet hermetic in this location**: the current code deliberately imports 16 experiment-local modules/assets through its original `BASE` layout.

HF freezes the proven producer bytes and provenance. HG will remove that experiment-directory coupling while proving generated R5..R27 capsules remain byte-identical to the accepted authorities. Do not change the producer algorithm during that relocation.
