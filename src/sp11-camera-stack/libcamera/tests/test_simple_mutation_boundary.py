#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Offline structural smoke test of the patched Simple handler. Not a live proof."""
import argparse
from pathlib import Path

arg = argparse.ArgumentParser()
arg.add_argument("simple", type=Path)
a = arg.parse_args()
s = a.simple.read_text()

def segment(begin: str, end: str) -> str:
    assert s.count(begin) == 1, (begin, s.count(begin))
    i = s.index(begin)
    j = s.index(end, i + len(begin))
    return s[i:j]

match = segment("bool SimplePipelineHandler::matchDevice(",
                "bool SimplePipelineHandler::match(")
assert match.index("sp11Lease_.initialize(media->deviceNode())") < match.index(
    "locateSensors(media.get())")
assert match.index("sp11::ExperimentalLibcameraLease::allowActiveRoutingReset()") < match.index(
    "ret = resetRoutingTable(subdev.get())")
assert "sp11::sensorAllowed(sensor->name())" in match
assert match.index("sp11Lease_.neutralizeWhenIdle()") < match.index(
    "registerCamera(std::move(camera))")
assert "return false; /* Never continue after uncertain route. */" in match

link = segment("int SimpleCameraData::setupLinks()", "int SimpleCameraData::setupFormats(")
assert link.index("if (sp11Camss_)") < link.index(
    "return pipe()->setupSp11Links(sp11SensorName_)") < link.index(
    "link->setEnabled(false)")
assert link.index("return pipe()->setupSp11Links(sp11SensorName_)") < link.index(
    "sinkLink->setEnabled(true)")

config = segment("int SimplePipelineHandler::configure(",
                 "int SimplePipelineHandler::exportFrameBuffers(")
assert "utils::scope_exit" in config
assert "sp11Lease_.parkRouteUntilStart()" in config
assert config.count("return completeConfiguration()") == 2

start = segment("int SimplePipelineHandler::start(",
                "void SimplePipelineHandler::stopDevice(")
assert start.index("sp11Lease_.beforeStream(data->sp11SensorName_)") < start.index(
    "ret = video->streamOn()")
stop = segment("void SimplePipelineHandler::stopDevice(",
               "int SimplePipelineHandler::queueRequestDevice(")
assert stop.index("video->streamOff()") < stop.index("sp11Lease_.afterStream()")
assert 'sp11_camera_e004lm_libcamera=1' in (
    a.simple.parent / "sp11-libcamera-experimental-lease.h").read_text()
print("PASS: E004lm Simple mutation sites and lifecycle are guarded in source (offline structural smoke test)")
