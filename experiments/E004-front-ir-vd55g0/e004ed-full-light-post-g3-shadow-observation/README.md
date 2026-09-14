# E004ed — full-light post-G3 shadow observation

Fresh shadow-only observation with the side lights **and** main room light on. This follows E004ec, where side lights alone left all 21 eligible G4..G24 sources at `SHADOW_CAP_ACTIVE` (decision 2), with the best convergence still around 16.54B versus the 6.13B preview cap.

E004ed changes only the physical lighting condition. It uses the same canonical package and accepted front R27 production path with `post_g3_policy=shadow`. No post-G3 native write is authorized.

Success for the environmental proof means at least one `PROD_POST_G3_POLICY_SHADOW` marker appears. That marker is the safe shadow evidence that Windows-authoritative logic reached `APPLY_ONE_NATIVE` / decision 4 while the hardware write remained suppressed.
