# E004lh libcamera RGB path-filter build

Source-only patch to pinned clean libcamera v0.7.0. Filter RGB sensors before creating camera data, then filter BFS edges by exact approved endpoints/pads. Includes the separately verified IMX681 gain helper during build. Dirty reference checkout remains untouched.

This is not live admission: cached link flags, graph transaction lifecycle and exclusive/quiescent ownership remain unresolved at the native adapter boundary. No installation, enumeration or physical camera test is allowed by this build-only result.
