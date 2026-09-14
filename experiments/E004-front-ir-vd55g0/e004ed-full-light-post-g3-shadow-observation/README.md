# E004ed — full-light post-G3 shadow observation

Fresh shadow-only observation with the side lights **and** main room light on. This follows E004ec, where side lights alone left all 21 eligible G4..G24 sources at `SHADOW_CAP_ACTIVE` (decision 2), with the best convergence still around 16.54B versus the 6.13B preview cap.

E004ed changes only the physical lighting condition. It uses the same canonical package and accepted front R27 production path with `post_g3_policy=shadow`. No post-G3 native write is authorized.

Success for the environmental proof means at least one `PROD_POST_G3_POLICY_SHADOW` marker appears. That marker is the safe shadow evidence that Windows-authoritative logic reached `APPLY_ONE_NATIVE` / decision 4 while the hardware write remained suppressed.


## Full-light result

The full-room-light shadow run still produced no APPLY_ONE_NATIVE opportunity. All 21 eligible G4..G24 sources remained decision 2 / CAP_ACTIVE and zero later native writes occurred. The brighter scene did move the system materially toward the threshold: best convergence fell to 13566504370 from the side-light run's ~16.54B, versus the fixed preview cap 6133333088. The remaining margin is 7433171282. SP11 returned to Golden, the candidate was retired and the package was removed.
