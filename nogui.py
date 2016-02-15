#!/usr/bin/env python3
#
# How to run a simulation without using the gui


import threading
import time
from display_curve import DisplayCurve
from display_rock_sample import DisplayRS
from echantillon import RockSample, StratifiedRockSample
from compression import Compression



##rs = StratifiedRockSample(nlines = 55, ncols = 23, leq0 = 1, Rl = 0.94, A0 = 1,
##                          Ka = 1, E0 = 1, Ke = 1, F0cr = 0.032, D = 0.03,
##                          F1cr = 0.028, dip = 20, t0 = 4, t1 = 8)
rs = RockSample(nlines = 71, ncols = 31, leq0 = 1, Rl = 0.94, A0 = 1,
                Ka = 1, E0 = 1, Ke = 1, F0cr = 0.03, D = 0.1)

cpr = Compression(rs, F0x = 0, Kbc = 20, d0 = 0., delta_d = 0.005, max_comp = 50)

delta_comp_rate = 2

def draw_sample():
    "fonction d'affichage de l'echantillon"
    DisplayRS(rs, scale = 8, d = cpr.d)

iteration = 0
dFy = DisplayCurve(xlegend="\u03B5(%)", ylegend="Fy",
                   yscale = 10000, ymax = 0.05)

cpr.d += cpr.delt_d
strain = cpr.d / rs.h0 * 100
comp_rate = rs.comp_count / rs.nsprings * 100
comp_rate_next_display = 0

first_compacted_displayed = False

# Commencer la compression
while comp_rate < cpr.max_comp:
    iteration += 1

    test_comp_count = rs.comp_count
    cpr.solve()
    comp_rate = rs.comp_count / rs.nsprings * 100

    # Affichage
    dFy.add_point(strain, cpr.Fy)
    if not first_compacted_displayed and comp_rate > 0.:
        threading.Thread(target=draw_sample).start()
        first_compacted_displayed = True
        time.sleep(2)
    if comp_rate >= comp_rate_next_display:
        threading.Thread(target=draw_sample).start()
        comp_rate_next_display += delta_comp_rate
        time.sleep(2)

    print("\nIteration %5d: " % iteration)
    print("\tCompaction rate:", comp_rate)

    # Incrementer le deplacement si aucun ressort n'a ete compacte
    if cpr.rs.comp_count == test_comp_count:

        if cpr.d < 2:
            cpr.d += 0.5
        else :
            cpr.d += cpr.delt_d
        strain = cpr.d / rs.h0 * 100
        print("\tStrain: %f" % strain)

threading.Thread(target=draw_sample).start()
time.sleep(2)
print("Done.")
