# =============================================================================
# Chapter 3: Loads and Load Combinations
# Extracted from report_generator.py — DO NOT add business logic here.
# =============================================================================

from osdagbridge.core.utils.common import (
    KEY_BL_IRC_CLASS_SV,
    KEY_CB_LOAD,
    KEY_FOOTPATH,
    KEY_LL_CUSTOM_VEHICLES,
    KEY_LL_ECCENTRICITY,
    KEY_LL_FOOTPATH_PRESSURE_MODE,
    KEY_LL_FOOTPATH_PRESSURE_VALUE,
    KEY_LL_IRC_70R_BOGIE,
    KEY_LL_IRC_70R_TRACKED,
    KEY_LL_IRC_70R_WHEELED,
    KEY_LL_IRC_AA_TRACKED,
    KEY_LL_IRC_AA_WHEELED,
    KEY_LL_IRC_CLASS_A,
    KEY_LL_IRC_CLASS_FATIGUE,
    KEY_LL_IRC_CLASS_SV,
    KEY_MATERIAL_DECK_DENSITY,
    KEY_MATERIAL_GIRDER_DENSITY,
    KEY_PL_SELF_WEIGHT_FACTOR,
    KEY_RL_LOAD_VALUE,
    KEY_SL_DAMPING,
    KEY_SL_DEAD_LOAD_MODE,
    KEY_SL_DEAD_LOAD_VALUE,
    KEY_SL_HORIZONTAL_COEFF,
    KEY_SL_IMPORTANCE_FACTOR,
    KEY_SL_LIVE_LOAD_MODE,
    KEY_SL_LIVE_LOAD_VALUE,
    KEY_SL_SEISMIC_ZONE,
    KEY_SL_SOIL_TYPE,
    KEY_SL_SPECTRAL_COEFF,
    KEY_SL_TIME_PERIOD,
    KEY_SL_VERTICAL_COEFF,
    KEY_SL_ZONE_FACTOR,
    KEY_SPAN,
    KEY_TL_BRIDGE_TEMP_MAX,
    KEY_TL_BRIDGE_TEMP_MIN,
    KEY_TL_HIGHEST_MAX_TEMP,
    KEY_TL_LOWEST_MIN_TEMP,
    KEY_TL_TEMP_FALL,
    KEY_TL_TEMP_RISE,
    KEY_WC_MATERIAL,
    KEY_WC_THICKNESS,
    KEY_WL_AVG_EXPOSED_HEIGHT,
    KEY_WL_BASIC_WIND_SPEED,
    KEY_WL_HOURLY_MEAN_WIND,
    KEY_WL_HOURLY_WIND_PRESSURE,
    KEY_WL_LONGITUDINAL_WIND_FORCE,
    KEY_WL_TERRAIN_TYPE,
    KEY_WL_TRANSVERSE_WIND_FORCE,
    KEY_WL_VERTICAL_WIND_FORCE
)

from osdagbridge.core.reports.report_utils import _tex, _render_value, _long_table

def ch3_loads(input_dict):
    from osdagbridge.core.utils.codes.irc6_2017 import IRC6_2017
    try:
        span_m = float(input_dict.get(KEY_SPAN))
        im_a = 1.0 + IRC6_2017.cl_208_2_impact_factor(span_m)
        im_aa = 1.0 + IRC6_2017.cl_208_3_impact_factor(span_m)
    except (TypeError, ValueError):
        im_a = im_aa = None

    # (input key, vehicle, total load kN, impact factor, braking considered?)
    # Code functions give wheel loads in N (SV in kN); vehicles without a
    # function use their IRC 6 gross weight in tonnes x g.
    g = 9.81
    irc_vehicles = [
        (KEY_LL_IRC_CLASS_A, "Class A",
         sum(IRC6_2017.cl_204_1_ClassA_vehicle()['wheel_loads']) / 1000.0, im_a, True),
        (KEY_LL_IRC_70R_WHEELED, "Class 70R (Wheeled)",
         sum(IRC6_2017.cl_204_1_Class70R_vehicle_wheel()['wheel_loads']) / 1000.0, im_aa, True),
        (KEY_LL_IRC_70R_TRACKED, "Class 70R (Tracked)", 70 * g, im_aa, True),
        (KEY_LL_IRC_70R_BOGIE, "Class 70R (Bogie)", 40 * g, im_aa, True),
        (KEY_LL_IRC_AA_WHEELED, "Class AA (Wheeled)", 40 * g, im_aa, True),
        (KEY_LL_IRC_AA_TRACKED, "Class AA (Tracked)", 70 * g, im_aa, True),
        (KEY_LL_IRC_CLASS_SV, "Class SV",
         IRC6_2017.cl_204_5_1_special_vehicle()['total_load_kN'], None,
         bool(input_dict.get(KEY_BL_IRC_CLASS_SV))),
        (KEY_LL_IRC_CLASS_FATIGUE, "Class Fatigue",
         sum(IRC6_2017.cl_204_6_fatigue_load()['wheel_loads']) / 1000.0, None, False),
    ]
    vehicles = [(name, load, im, brk) for key, name, load, im, brk in irc_vehicles if input_dict.get(key)]

    for c in input_dict.get(KEY_LL_CUSTOM_VEHICLES) or []:
        if isinstance(c, dict) and c.get('name'):
            loads = c.get('axle_loads') or []
            im = c.get('impact_factor')
            vehicles.append((c['name'], sum(loads) if loads else None,
                             1.0 + im if im is not None else None, True))

    ecc = _render_value(input_dict, KEY_LL_ECCENTRICITY) or "---"
    ll_rows = []
    for name, load, im, brk in vehicles:
        ll_rows.append(
            _tex(name)
            + r" & " + (f"{load:.2f}" if load is not None else "---")
            + r" & " + (f"{im:.3f}" if im is not None else "---")
            + r" & " + ("Yes" if brk else "No")
            + r" & " + (f"{0.20 * load:.2f}" if brk and load is not None else "---")
            + r" & " + (ecc if brk else "---")
            + r" \\[\rowsep]" + "\n" + r"\hline"
        )
    if not ll_rows:
        ll_rows.append(r"\multicolumn{6}{|c|}{No vehicle selected} \\[\rowsep]" + "\n" + r"\hline")
    ll_rows_str = "\n".join(ll_rows)

    # Footpath live load (IRC 6 Cl. 206.1 or user value)
    if str(input_dict.get(KEY_FOOTPATH, "None")).strip().lower() == "none":
        fp_val, fp_basis = "---", "Not applicable (no footpath)"
    elif str(input_dict.get(KEY_LL_FOOTPATH_PRESSURE_MODE, "")).strip().lower() == "custom":
        fp_val, fp_basis = _render_value(input_dict, KEY_LL_FOOTPATH_PRESSURE_VALUE) or "---", "User-defined"
    else:
        fp_val, fp_basis = f"{IRC6_2017.cl_206_1_footway_load():.3f}", "IRC 6 Cl. 206.1"

    # Vz / Pz — prefer stored computed values; fall back to IRC6 Table 12
    vz_val = input_dict.get(KEY_WL_HOURLY_MEAN_WIND)
    pz_val = input_dict.get(KEY_WL_HOURLY_WIND_PRESSURE)
    if not vz_val or not pz_val:
        try:
            _vb  = input_dict.get(KEY_WL_BASIC_WIND_SPEED) or input_dict.get('wind_speed')
            _h   = input_dict.get(KEY_WL_AVG_EXPOSED_HEIGHT)
            _ter = {
                "Plain Terrain": "plain",
                "Terrain with Obstructions": "obstructed",
            }.get(str(input_dict.get(KEY_WL_TERRAIN_TYPE, "")).strip(), "plain")
            _res = IRC6_2017.table_12(float(_h), _ter, float(_vb))
            if not vz_val:
                vz_val = _res.get("Vz")
            if not pz_val:
                pz_val = _res.get("Pz")
        except Exception:
            pass
    vz_str = f"{float(vz_val):.2f} m/s" if vz_val not in (None, "") else "N/A"
    pz_str = f"{float(pz_val):.2f} N/m²" if pz_val not in (None, "") else "N/A"

    # Table 3.5 — Seismic: prefer stored computed values; fall back to IRC6 cl_218_5_1
    sl_zone_factor = input_dict.get(KEY_SL_ZONE_FACTOR)
    sl_spectral    = input_dict.get(KEY_SL_SPECTRAL_COEFF)
    sl_ah          = input_dict.get(KEY_SL_HORIZONTAL_COEFF)
    sl_av          = input_dict.get(KEY_SL_VERTICAL_COEFF)
    if not sl_ah or not sl_zone_factor:
        try:
            _zone = input_dict.get(KEY_SL_SEISMIC_ZONE) or input_dict.get('seismic_zone')
            _zmap = {"1": "I", "2": "II", "3": "III", "4": "IV", "5": "V"}
            _z    = str(_zone).strip().upper()
            if _z.isdigit():
                _z = _zmap.get(_z)
            _smap = {"Type I – Rocky or Hard": 1, "Type II – Medium Soil": 2, "Type III – Soft Soil": 3}
            _st   = _smap.get(str(input_dict.get(KEY_SL_SOIL_TYPE, "")), 1)
            _tp   = input_dict.get(KEY_SL_TIME_PERIOD)
            _damp = input_dict.get(KEY_SL_DAMPING) or "5"
            _dl_v = input_dict.get(KEY_SL_DEAD_LOAD_VALUE)
            _ll_v = input_dict.get(KEY_SL_LIVE_LOAD_VALUE)
            _dead = float(_dl_v) if str(input_dict.get(KEY_SL_DEAD_LOAD_MODE, "")) == "Custom" and _dl_v else 0.0
            _live = float(_ll_v) if str(input_dict.get(KEY_SL_LIVE_LOAD_MODE, "")) == "Custom" and _ll_v else 0.0
            _res  = IRC6_2017.cl_218_5_1(zone=f"Zone {_z}", soil_type=_st, dead_load_kN=_dead,
                        live_load_kN=_live, period_T=float(_tp) if _tp else None,
                        damping_percent=float(_damp))
            if not sl_zone_factor:
                sl_zone_factor = _res.get("Z")
            if not sl_spectral:
                sl_spectral    = _res.get("Sa_g_adjusted")
            if not sl_ah:
                sl_ah          = _res.get("Ah")
            if not sl_av:
                sl_av          = round(_res.get("Ah", 0) * 2 / 3, 4)
        except Exception:
            pass

    def _sl(v, unit=""):
        return f"{float(v):.4f}{unit}" if v not in (None, "") else "N/A"

    # Table 3.6 — Temperature: compute effective bridge temp range from shade temps
    tl_temp_min = tl_temp_max = tl_rise = tl_fall = "N/A"
    try:
        _tmax = input_dict.get(KEY_TL_HIGHEST_MAX_TEMP) or input_dict.get('shade_temp_max')
        _tmin = input_dict.get(KEY_TL_LOWEST_MIN_TEMP)  or input_dict.get('shade_temp_min')
        if _tmax and _tmin:
            _res    = IRC6_2017.cl_215_2_effective_bridge_temperature(
                          float(_tmax), float(_tmin), 'metallic', False)
            _bt_min = _res.get('T_min', 0)
            _bt_max = _res.get('T_max', 0)
            _mean   = (_bt_max + _bt_min) / 2.0
            tl_temp_min = f"{_bt_min:.2f}"
            tl_temp_max = f"{_bt_max:.2f}"
            tl_rise     = f"{_bt_max - _mean:.2f}"
            tl_fall     = f"{_mean - _bt_min:.2f}"
    except Exception:
        pass

    # --- Table 3.7: Load Combinations (dynamically generated from IRC 6) ---
    _LOAD_LABEL_MAP = {
        'dead_load':         'DL',
        'surfacing':         'SIDL',
        'live_load':         'LL',
        'wind_load':         'WL',
        'thermal_load':      'TL',
        'vehicle_collision': 'VC',
        'barge_impact':      'BI',
        'floating_bodies':   'FB',
        'seismic':           'EQ',
    }

    def _fmt_factors(factors):
        """Format a factors dict into a compact load-case string for the table."""
        parts = []
        for load, val in factors.items():
            label = _LOAD_LABEL_MAP.get(load, load.upper())
            if isinstance(val, dict):  # permanent load with adding/relieving
                add = val.get('adding')
                rel = val.get('relieving')
                add_s = f"{add:.2f}" if add is not None else '--'
                rel_s = f"{rel:.2f}" if rel is not None else '--'
                parts.append(f"{label}({add_s}/{rel_s})")
            else:
                if val is None:
                    continue  # skip N/A factors
                parts.append(f"{label}({val:.2f})")
        return ' + '.join(parts)

    uls_combos = IRC6_2017.uls_load_combinations()
    sls_combos = IRC6_2017.sls_load_combinations()
    lc_rows = []
    for i, combo in enumerate(uls_combos, start=1):
        cases = _fmt_factors(combo['factors'])
        lc_rows.append(
            f"ULS-{i:02d}" + r" & " + cases + r" \\[\rowsep]" + "\n"
            + r"\hline"
        )
    for i, combo in enumerate(sls_combos, start=1):
        cases = _fmt_factors(combo['factors'])
        lc_rows.append(
            f"SLS-{i:02d}" + r" & " + cases + r" \\[\rowsep]" + "\n"
            + r"\hline"
        )

    lc_rows_str = "\n".join(lc_rows)

    return r"""
\chapter{Loads and Load Combinations}

This section summarizes all loads applied to the bridge and the load combinations considered for analysis and design.

""" + _long_table(r"|L{5.5cm}|p{10.0cm}|", r"Dead Load -- Self Weight", r"\textbf{parameter} & \textbf{value} \\", r"""
\textnormal{Steel Self-Weight Applied} & """ + (_render_value(input_dict, KEY_MATERIAL_GIRDER_DENSITY, ' kN/m\\textsuperscript{3}')) + r""" \\[\rowsep]
\hline
\textnormal{Concrete Deck Weight} & """ + (_render_value(input_dict, KEY_MATERIAL_DECK_DENSITY, ' kN/m\\textsuperscript{3}')) + r""" \\[\rowsep]
\hline
\textnormal{Self-Weight Factor} & """ + (_render_value(input_dict, KEY_PL_SELF_WEIGHT_FACTOR)) + r""" \\[\rowsep]
\hline
""") + r"""

""" + _long_table(r"|L{5.5cm}|p{10.0cm}|", r"Dead Load for Surfacing (DW)", r"\textbf{parameter} & \textbf{value} \\", r"""
\textnormal{Wearing Course Load} & """ + (_render_value(input_dict, KEY_WC_MATERIAL)) + r""" x """ + (_render_value(input_dict, KEY_WC_THICKNESS)) + r""" \\[\rowsep]
\hline
\textnormal{Additional SIDL (Crash Barrier)} & """ + (_render_value(input_dict, KEY_CB_LOAD)) + r""" kN/m per barrier \\[\rowsep]
\hline
\textnormal{Railing Load} & """ + (_render_value(input_dict, KEY_RL_LOAD_VALUE)) + r""" kN/m\sdstar{} \\[\rowsep]
\hline
""") + r"""

""" + _long_table(r"|L{2.8cm}|C{2.2cm}|C{1.8cm}|C{2.4cm}|C{1.7cm}|C{2.4cm}|", r"Vehicle Live Loads (LL)", r"""
\textbf{Vehicle} & \textbf{Total Load (kN)} & \textbf{Impact Factor} & \multicolumn{3}{c|}{\textbf{Braking Load}} \\
\cline{4-6}
 & & & \textbf{Considered?} & \textbf{Value (kN)} & \textbf{Eccentricity (m)} \\
""", r"""
""" + ll_rows_str + r"""
""") + r"""
\noindent\textit{Note: Braking load = 20\% of the vehicle load (IRC 6 Cl. 211.2), acting at the eccentricity above the deck (Cl. 211.3).}

""" + _long_table(r"|L{5.5cm}|C{3.0cm}|C{2.5cm}|", r"Footpath Live Load", r"\textbf{Parameter} & \textbf{Value} & \textbf{Unit} \\", r"""
\textnormal{Footpath Live Load} & """ + fp_val + r""" & kN/m\textsuperscript{2} \\[\rowsep]
\hline
\textnormal{Basis} & \multicolumn{2}{c|}{""" + fp_basis + r"""} \\[\rowsep]
\hline
""") + r"""

""" + _long_table(r"|L{5.5cm}|p{10.0cm}|", r"Wind Load (WL) --- per IRC 6", r"\textbf{parameter} & \textbf{value} \\", r"""
\textnormal{Basic Wind Speed, Vb} & """ + (_render_value(input_dict,'wind_speed', ' m/s')) + r""" [from Project Location] \\[\rowsep]
\hline
\textnormal{Terrain Type} & """ + (_render_value(input_dict, KEY_WL_TERRAIN_TYPE)) + r""" \\[\rowsep]
\hline
\textnormal{Average Exposed Height, H (m)} & """ + (_render_value(input_dict, KEY_WL_AVG_EXPOSED_HEIGHT, ' m')) + r""" \\[\rowsep]
\hline
\textnormal{Hourly Mean Wind Speed, Vz} & """ + (_render_value(input_dict, KEY_WL_HOURLY_MEAN_WIND, ' m/s')) + r""" \\[\rowsep]
\hline
\textnormal{Hourly Wind Pressure, Pz} & """ + (_render_value(input_dict, KEY_WL_HOURLY_WIND_PRESSURE, ' N/m\\textsuperscript{2}')) + r""" \\[\rowsep]
\hline
\textnormal{Transverse Wind Force} & """ + (_render_value(input_dict, KEY_WL_TRANSVERSE_WIND_FORCE, ' kN')) + r""" \\[\rowsep]
\hline
\textnormal{Longitudinal Wind Force} & """ + (_render_value(input_dict, KEY_WL_LONGITUDINAL_WIND_FORCE, ' kN')) + r""" \\[\rowsep]
\hline
\textnormal{Vertical Wind Force} & """ + (_render_value(input_dict, KEY_WL_VERTICAL_WIND_FORCE, ' kN')) + r""" \\[\rowsep]
\hline
""") + r"""

""" + _long_table(r"|L{5.5cm}|p{10.0cm}|", r"Earthquake Load (EL) --- per IRC 6", r"\textbf{parameter} & \textbf{value} \\", r"""
\textnormal{Seismic Zone} & """ + (_render_value(input_dict,'seismic_zone')) + r""" [from Project Location] \\[\rowsep]
\hline
\textnormal{Zone Factor, Z} & """ + (_render_value(input_dict, KEY_SL_ZONE_FACTOR)) + r""" \\[\rowsep]
\hline
\textnormal{Importance Factor, I} & """ + (_render_value(input_dict, KEY_SL_IMPORTANCE_FACTOR)) + r""" \\[\rowsep]
\hline
\textnormal{Type of Soil} & """ + (_render_value(input_dict, KEY_SL_SOIL_TYPE)) + r""" \\[\rowsep]
\hline
\textnormal{Sa/g} & """ + (_render_value(input_dict, KEY_SL_SPECTRAL_COEFF)) + r""" \\[\rowsep]
\hline
\textnormal{Horizontal Seismic Coefficient, Ah} & """ + (_render_value(input_dict, KEY_SL_HORIZONTAL_COEFF)) + r""" \\[\rowsep]
\hline
\textnormal{Vertical Seismic Coefficient, Av} & """ + (_render_value(input_dict, KEY_SL_VERTICAL_COEFF)) + r""" \\[\rowsep]
\hline
\textnormal{Horizontal Seismic Force (longitudinal)} & """ + '' + r""" kN \\[\rowsep]
\hline
\textnormal{Horizontal Seismic Force (transverse)} & """ + '' + r""" kN \\[\rowsep]
\hline
""") + r"""

""" + _long_table(r"|L{5.5cm}|p{10.0cm}|", r"Temperature Load (TL) --- per IRC 6", r"\textbf{parameter} & \textbf{value} \\", r"""
\textnormal{Maximum Shade Temperature} & """ + (_render_value(input_dict,'shade_temp_max')) + r""" $^\circ$C \\[\rowsep]
\hline
\textnormal{Minimum Shade Temperature} & """ + (_render_value(input_dict,'shade_temp_min')) + r""" $^\circ$C \\[\rowsep]
\hline
\textnormal{Effective Bridge Temp. Range} & """ + (_render_value(input_dict, KEY_TL_BRIDGE_TEMP_MIN)) + r""" to """ + (_render_value(input_dict, KEY_TL_BRIDGE_TEMP_MAX)) + r""" $^\circ$C \\[\rowsep]
\hline
\textnormal{Temperature Rise / Fall for Design} & +""" + (_render_value(input_dict, KEY_TL_TEMP_RISE)) + r""" $^\circ$C / \textminus{}""" + (_render_value(input_dict, KEY_TL_TEMP_FALL)) + r""" $^\circ$C \\[\rowsep]
\hline
""") + r"""

""" + _long_table(r"|C{4.0cm}|p{11.5cm}|", r"Load Combinations", r"\textbf{Combination ID} & \textbf{Load Cases} \\[\rowsep]", r"""
""" + lc_rows_str + r"""
""") + r"""

\noindent\textit{Note: All IRC 6 load combinations are auto-generated by OsdagBridge. User-defined custom combinations, if any, are appended.}
"""


