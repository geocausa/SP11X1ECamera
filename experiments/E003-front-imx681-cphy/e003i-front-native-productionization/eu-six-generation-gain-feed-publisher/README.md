# E003i-EU — six-generation C gain-feed publisher correction

Status: **PASS OFFLINE / NO CAMERA RUNTIME.**

ET exposed a latent integration defect without reopening the closed EN stage: the nine-frame helper publishes CQ residual gain for G1..G6, but the copied C publisher still rejected every generation above G3 with -EINVAL.

EU is a fresh isolated correction. It changes only the publisher validation upper bound from G3 to G6, preserves the wire ABI and request identity (request = generation + 3), and proves the real compiled C publisher accepts G1..G6 while rejecting G7 and malformed request identity.

No live camera attempt is performed here. A future live retry must use a new one-shot candidate identity and depend on EU rather than modifying or reusing ET.
