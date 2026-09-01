# E003h 0072 IQ-provider FIFO regression candidate

Bounded regression of accepted 0071 live V4L2 requeue through the new 0072 software IQ FIFO.

No new camera hardware action is introduced. Request4 remains the proven bootstrap capsule; exact request5 is copied, validated, enqueued, dequeued, then handed to the unchanged runner. No request6 is present or authorized.
