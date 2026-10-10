#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Generate capture-front-ae.cpp (manual tone check + AE phase) from the
front pattern capture tool, so both share one reviewed reduction/IO path."""
from pathlib import Path
HERE = Path(__file__).resolve().parent
src = (HERE.parent / "front-pattern/capture-front-pattern.cpp").read_text()


def rep(a, b):
    global src
    assert src.count(a) == 1, a[:60]
    src = src.replace(a, b)


rep(""" * SP11 front (imx681) calibration capture against a displayed pattern loop.
 *
 * Manual controls only. A fixed exposure/analogue/digital gain ladder is
 * stepped by completed-frame count.""", """ * SP11 front (imx681) validation capture against a displayed pattern loop.
 *
 * Phase 0 uses fixed manual controls (tone/colour check against the Windows
 * fixed-exposure reference); phase 1 enables pipeline automatic exposure
 * (AE check against the Windows automatic reference). Per-frame applied
 * exposure, gains and AeState are written to meta.csv.""")
rep("""struct Phase { int32_t lines; float again, dgain; };
const Phase kPhases[] = {
	{ 3546, 2.0f, 1.0f }, { 3546, 4.0f, 1.0f }, { 3546, 8.0f, 1.0f },
	{ 3546, 16.0f, 1.0f }, { 3546, 16.0f, 2.0f },
};""", """struct Phase { int32_t lines; float again, dgain; bool automatic; };
const Phase kPhases[] = { { 3546, 16.0f, 1.0f, false }, { 0, 0.0f, 0.0f, true } };""")
rep("""void setPhase(ControlList &c, const Phase &p)
{
	c.set(controls::ExposureTime, exposureUs(p.lines));
	c.set(controls::AnalogueGain, p.again);
	c.set(controls::DigitalGain, p.dgain);
}""", """void setPhase(ControlList &c, const Phase &p)
{
	if (p.automatic) {
		c.set(controls::AeEnable, true);
		return;
	}
	c.set(controls::AeEnable, false);
	c.set(controls::ExposureTime, exposureUs(p.lines));
	c.set(controls::AnalogueGain, p.again);
	c.set(controls::DigitalGain, p.dgain);
}
struct Meta { uint32_t sequence; int32_t exposure_us; float again, dgain; int32_t ae_state, ae_enable; };""")
rep("""			/* Record the applied phase from metadata when it disagrees. */
			const auto &md = request->metadata();
			auto ag = md.get(controls::AnalogueGain);
			auto dg = md.get(controls::DigitalGain);
			if (ag && dg) {
				unsigned applied = kPhaseCount;
				for (unsigned i = 0; i < kPhaseCount; i++)
					if (std::fabs(*ag - kPhases[i].again) < 0.05f * kPhases[i].again &&
					    std::fabs(*dg - kPhases[i].dgain) < 0.02f)
						applied = i;
				if (applied != r.phase) {
					mismatches_++;
					r.phase = applied == kPhaseCount ? 0xffffffffu : applied;
				}
			}""", """			const auto &md = request->metadata();
			Meta m{ r.sequence, md.get(controls::ExposureTime).value_or(-1),
				md.get(controls::AnalogueGain).value_or(-1.0f),
				md.get(controls::DigitalGain).value_or(-1.0f),
				md.get(controls::AeState).value_or(-1),
				int32_t(md.get(controls::AeEnable).value_or(false)) };
			meta_.push_back(m);
			/* Phase 0 frames whose applied controls are not the manual values
			 * yet (transition) are marked invalid. */
			if (r.phase == 0 && (std::fabs(m.again - kPhases[0].again) > 0.05f * kPhases[0].again ||
					     m.exposure_us != exposureUs(kPhases[0].lines))) {
				mismatches_++;
				r.phase = 0xffffffffu;
			}""")
rep("""		need(!std::fclose(f), "records close");
""", """		need(!std::fclose(f), "records close");
		std::string mpath = dir_ + "/meta.csv";
		FILE *mf = std::fopen(mpath.c_str(), "wx");
		need(mf, "meta file");
		std::fprintf(mf, "sequence,exposure_us,again,dgain,ae_state,ae_enable\\n");
		for (const Meta &m : meta_)
			std::fprintf(mf, "%u,%d,%.4f,%.4f,%d,%d\\n", m.sequence, m.exposure_us, m.again, m.dgain,
				     m.ae_state, m.ae_enable);
		need(!std::fclose(mf), "meta close");
""")
rep("""	std::vector<Record> records_;""", """	std::vector<Record> records_;
	std::vector<Meta> meta_;""")
rep("""		if (keep_.size() < 2 && (completed_ == perPhase_ + 40 || completed_ == 3 * perPhase_ + perPhase_ / 2)) {""",
    """		if (keep_.size() < 2 && (completed_ == perPhase_ / 2 || completed_ == perPhase_ + perPhase_ / 2)) {""")
rep("""strtoul(pp, nullptr, 10)) : 1650;""", """strtoul(pp, nullptr, 10)) : 1800;""")
rep("""\t\tmanager.stop();\n\t\treturn 0;""", """\t\tcamera.reset();\n\t\tmanager.stop();\n\t\treturn 0;""")
rep('"SP11 front pattern calibration capture', '"SP11 front AE/tone validation capture')
src = src.replace('PASS_FRONT_PATTERN_CAPTURE', 'PASS_FRONT_AE_CAPTURE').replace(
    'PARTIAL_FRONT_PATTERN_CAPTURE', 'PARTIAL_FRONT_AE_CAPTURE').replace('FRONT_PATTERN_FAILED', 'FRONT_AE_FAILED')
rep("""\t\t\t\t  << ",\\"dgain\\":" << kPhases[i].dgain << "}";""",
    """\t\t\t\t  << ",\\"dgain\\":" << kPhases[i].dgain << ",\\"automatic\\":" << kPhases[i].automatic << "}";""")
(HERE / "capture-front-ae.cpp").write_text(src)
print("WROTE", HERE / "capture-front-ae.cpp")
