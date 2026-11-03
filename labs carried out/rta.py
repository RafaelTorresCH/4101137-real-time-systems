#!/usr/bin/env python3
"""
Week 6 — Schedulability & Response Time Analysis (RTA) Script
Course: 4101137 Real-Time Systems (UNAL)
Implements Buttazzo Fig. 4.17 iterative RTA with blocking B_i (Theorem 7.2):
    R_i = C_i + B_i + sum_{h < i} ceil(R_i / T_h) * C_h
"""
import math
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Task:
    name: str
    prio: int
    C_us: float   # Measured worst-case execution time (us)
    T_us: float   # Period (us)
    D_us: float   # Relative deadline (us)
    B_us: float = 0.0  # Maximum blocking time from lower-priority tasks via PIP mutex (us)


def utilization_tests(tasks: List[Task]) -> Tuple[float, float, float]:
    """Return (U_total, Liu_Layland_bound, Hyperbolic_product)."""
    n = len(tasks)
    u_list = [t.C_us / t.T_us for t in tasks]
    u_total = sum(u_list)
    ll_bound = n * (2.0 ** (1.0 / n) - 1.0)
    hyp_prod = 1.0
    for u in u_list:
        hyp_prod *= (u + 1.0)
    return u_total, ll_bound, hyp_prod


def rta_task(tasks: List[Task], idx: int) -> Tuple[float, List[float], bool]:
    """Iterative Response Time Analysis (Buttazzo Fig. 4.17 + Theorem 7.2 blocking B_i)."""
    ti = tasks[idx]
    r_prev = ti.C_us + ti.B_us
    steps = [r_prev]
    while True:
        interference = sum(
            math.ceil(r_prev / th.T_us) * th.C_us for th in tasks[:idx]
        )
        r_new = ti.C_us + ti.B_us + interference
        steps.append(r_new)
        if r_new > ti.D_us:
            return r_new, steps, False
        if abs(r_new - r_prev) < 1e-6:
            return r_new, steps, True
        r_prev = r_new


def run_suite(title: str, tasks: List[Task]) -> None:
    print(f"=== {title} ===")
    u_tot, ll_bound, hyp_prod = utilization_tests(tasks)
    print(f"Tasks (n={len(tasks)}): U = {u_tot:.5f} ({u_tot*100:.2f}%)")
    print(f"  Liu & Layland bound n(2^(1/n)-1) = {ll_bound:.5f} -> {'PASS (guaranteed RM)' if u_tot <= ll_bound else 'INCONCLUSIVE (above bound, run RTA)'}")
    print(f"  Hyperbolic bound prod(U_i + 1)   = {hyp_prod:.5f} <= 2.0 -> {'PASS (guaranteed RM)' if hyp_prod <= 2.0 else 'INCONCLUSIVE (above 2.0, run RTA)'}")
    print(f"  EDF exact bound U <= 1.0         = {u_tot:.5f} <= 1.0 -> {'PASS (schedulable under EDF)' if u_tot <= 1.0 else 'FAIL'}")
    print(f"{'Task':<18} {'Prio':>4} {'C (us)':>9} {'T (us)':>10} {'D (us)':>10} {'B (us)':>8} {'R (us)':>10} {'Verdict'}")
    print("-" * 82)
    for i, t in enumerate(tasks):
        r, steps, ok = rta_task(tasks, i)
        verdict = "MEETS (R <= D)" if ok else "MISSES (R > D)"
        print(f"{t.name:<18} {t.prio:>4d} {t.C_us:>9.2f} {t.T_us:>10.1f} {t.D_us:>10.1f} {t.B_us:>8.1f} {r:>10.2f} {verdict}")
    print()


if __name__ == "__main__":
    # 1. Book Fig. 4.13 (tau1: C=2 ms, T=5 ms; tau2: C=4 ms, T=7 ms)
    fig413 = [
        Task("tau1 (Fig 4.13)", 2, 2000.0, 5000.0, 5000.0),
        Task("tau2 (Fig 4.13)", 3, 4000.0, 7000.0, 7000.0),
    ]
    run_suite("1. Buttazzo Fig. 4.13 (RM vs EDF)", fig413)

    # 2. SoilSense Node on ESP32-C6 (measured C_i, no lock contention B=0)
    node_no_lock = [
        Task("sampling_tid",  2,   41.19,    1000.0,    1000.0, B_us=0.0),
        Task("control_tid",   3,   21.00,   10000.0,   10000.0, B_us=0.0),
        Task("flow_wq",       5,   85.00,   20000.0,   20000.0, B_us=0.0),
        Task("display_tid",   7,   35.56,   50000.0,   50000.0, B_us=0.0),
        Task("telemetry_tid", 8, 6000.00, 1000000.0, 1000000.0, B_us=0.0),
    ]
    run_suite("2. SoilSense Node (ESP32-C6 Measured C_i, B = 0 us)", node_no_lock)

    # 3. SoilSense Node with PIP Mutex Blocking B_ctrl = 500 us (Task B)
    node_pip_mutex = [
        Task("sampling_tid",  2,   41.19,    1000.0,    1000.0, B_us=0.0),
        Task("control_tid",   3,   21.00,   10000.0,   10000.0, B_us=500.0),
        Task("flow_wq",       5,   85.00,   20000.0,   20000.0, B_us=0.0),
        Task("display_tid",   7,   35.56,   50000.0,   50000.0, B_us=0.0),
        Task("telemetry_tid", 8, 6000.00, 1000000.0, 1000000.0, B_us=0.0),
    ]
    run_suite("3. SoilSense Node with PIP Mutex (B_ctrl = 500 us)", node_pip_mutex)

    # 4. SoilSense Node + Daniela's two additional sensors (U ≈ 0.72 above console)
    daniela_set = [
        Task("sampling_tid",     2,   41.19,    1000.0,    1000.0, B_us=0.0),
        Task("control_tid",      3,   21.00,   10000.0,   10000.0, B_us=500.0),
        Task("daniela_moist",    4, 1500.00,    4000.0,    4000.0, B_us=0.0),
        Task("flow_wq",          5,   85.00,   20000.0,   20000.0, B_us=0.0),
        Task("daniela_ec_temp",  6, 2900.00,   10000.0,   10000.0, B_us=0.0),
        Task("display_tid",      7,   35.56,   50000.0,   50000.0, B_us=0.0),
        Task("telemetry_tid",    8, 6000.00, 1000000.0, 1000000.0, B_us=0.0),
    ]
    run_suite("4. SoilSense Node + Daniela's 2 Sensors (U ≈ 0.72, slide 16)", daniela_set)

    # 5. High-load Daniela case (U ≈ 0.85 > Liu & Layland bound, slide 5)
    daniela_high = [
        Task("sampling_tid",     2,   41.19,    1000.0,    1000.0, B_us=0.0),
        Task("control_tid",      3,   21.00,   10000.0,   10000.0, B_us=500.0),
        Task("daniela_moist",    4, 1800.00,    4000.0,    4000.0, B_us=0.0),
        Task("flow_wq",          5,   85.00,   20000.0,   20000.0, B_us=0.0),
        Task("daniela_ec_temp",  6, 3450.00,   10000.0,   10000.0, B_us=0.0),
        Task("display_tid",      7,   35.56,   50000.0,   50000.0, B_us=0.0),
        Task("telemetry_tid",    8, 6000.00, 1000000.0, 1000000.0, B_us=0.0),
    ]
    run_suite("5. SoilSense Node + Daniela High Load (U ≈ 0.85 > ln 2, slide 5)", daniela_high)

