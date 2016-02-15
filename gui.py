#!/usr/bin/env python3
#
# Meta-widget made of a label, an entry and a button. Clicking on the
# button opens a pop-up window with a user defined help message.
# Copyright (C) 2011 Pierre Knobel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import tkinter
import threading
import time
from labelentry import LabelEntry
from display_curve import DisplayCurve
from display_rock_sample import DisplayRS
from echantillon import RockSample, StratifiedRockSample
from compression import Compression



class ParamGUI(tkinter.Tk):

    def __init__(self, parent = None):
        tkinter.Tk.__init__(self,parent)
        self.parent = parent

        # layout manager:
        self.grid()

        # Rock sample parameters:
        # L      A0    F0cr
        # C      E0    D
        # leq0   Ka
        # Rl     Ke
        rock_frame = tkinter.Frame(self, relief='ridge', bd = 2)
        rock_frame.grid(column=0, row=0, sticky='EW', columnspan=2, padx = 3,
                        pady =3)

        rock_label = tkinter.Label(rock_frame, text = "Rock sample parameters",
                                   font = "Helvetica 14 bold", fg = '#009')
        rock_label.grid(column=0, row=0, columnspan=3)

        self.L = LabelEntry(rock_frame, label_text = "Lines", val_type = int,
                            default_val = 61, min_val = 3)
        self.L.doc = "Number of lines in the spring network"
        self.L.grid(column=0, row=1, sticky='EW', padx = 2)

        self.C = LabelEntry(rock_frame, label_text = "Columns", val_type = int,
                             default_val = 20, min_val = 3)
        self.C.doc = "Number of columns in the spring network"
        self.C.grid(column=0, row=2, sticky='EW', padx = 2)

        self.leq0 = LabelEntry(rock_frame, label_text = "leq0", min_val = 0.001,
                               val_type = float, default_val = 1.)
        self.leq0.doc = "Equilibrium lenght for a spring before compaction"
        self.leq0.grid(column=0, row=3, sticky='EW', padx = 2)

        self.Rl = LabelEntry(rock_frame, label_text = "Rl", val_type = float,
                             default_val = 0.94, min_val = 0.)
        self.Rl.doc = "Ratio leq_new / leq0, where leq_new is the equilibrium "
        self.Rl.doc += "length of a compacted spring."
        self.Rl.grid(column=0, row=4, sticky='EW', padx = 2)

        self.A0 = LabelEntry(rock_frame, label_text = "A0", val_type = float,
                             default_val = 1., min_val = 0.00001)
        self.A0.doc = "Initial cross-sectional area of non-compacted spring."
        self.A0.grid(column=1, row=1, sticky='EW', padx = 2)

        self.E0 = LabelEntry(rock_frame, label_text = "E0", val_type = float,
                             default_val = 1., min_val = 0.00001)
        self.E0.doc = "Initial Young modulus"
        self.E0.grid(column=1, row=2, sticky='EW', padx = 2)

        self.Ka = LabelEntry(rock_frame, label_text = "Ka", val_type = float,
                             default_val = 1., min_val=0.00001)
        self.Ka.doc = "Ratio Anew / A0 where Anew is the cross-sectional area " 
        self.Ka.doc += "for  a compacted spring"
        self.Ka.grid(column=1, row=3, sticky='EW', padx = 2)

        self.Ke = LabelEntry(rock_frame, label_text = "Ke", val_type = float,
                             default_val = 1, min_val=0.00001)
        self.Ka.doc = "Elastic ratio Enew / E0 where Enew is the young modulus" 
        self.Ka.doc += " for a compacted spring"
        self.Ke.grid(column=1, row=4, sticky='EW', padx = 2)

        self.F0cr = LabelEntry(rock_frame, label_text = "F0cr",
                               val_type = float, default_val = 0.03,
                               min_val = 0.000001)
        self.F0cr.doc = "Mean value of the stress threshold distribution"
        self.F0cr.grid(column=2, row=1, sticky='EW', padx = 2)

        self.D = LabelEntry(rock_frame, label_text = "D",val_type = float,
                            default_val = 0.01, min_val = 0)
        self.D.doc = "Degree of disorder in the stress threshold distribution "
        self.D.doc += "(ratio \u0394Fcr / F0cr where \u0394Fcr is the standard"
        self.D.doc += " deviation of the distribution)"
        self.D.grid(column=2, row=2, sticky='EW', padx = 2)

        # Compression parameters:
        # F0x
        # Kbc
        # delt_d
        # max comp
        
        comp_frame = tkinter.Frame(self, relief='ridge', bd = 2)
        comp_frame.grid(column=0, row=1, sticky='NSEW', padx = 3, pady =3)

        comp_label = tkinter.Label(comp_frame, text = "Compression parameters",
                                   font = "Helvetica 14 bold", fg = '#009')
        comp_label.grid(column=0, row=0)

        self.F0x = LabelEntry(comp_frame, label_text = "F0x", val_type = float,
                              default_val=0.)
        self.F0x.doc = "Horizontal confinement force"
        self.F0x.grid(column=0, row=1)

        self.Kbc = LabelEntry(comp_frame, label_text = "Kbc", val_type = float,
                              default_val = 20., min_val = 1)
        self.Kbc.doc = "Top and bottom boundary condition."
        self.Kbc.grid(column=0, row=2)

        self.d0 = LabelEntry(comp_frame, label_text = "d0",
                             val_type = float, default_val=0)
        self.d0.doc = "Initial displacement"
        self.d0.grid(column=0, row=3)

        self.delt_d = LabelEntry(comp_frame, label_text = "\u0394d",
                                 val_type = float, default_val=0.005,
                                 min_val = 0)
        self.delt_d.doc = "Displacement increment applied to the top and bottom"
        self.delt_d.doc += " boundaries between two iterations. A smaller value"
        self.delt_d.doc +=" will lead to a better approximation of a continuous"
        self.delt_d.doc += " compression (ideally no more than one spring "
        self.delt_d.doc += "should be compacted after each increment) but will "
        self.delt_d.doc += "also make the computation be more time-consuming."
        self.delt_d.grid(column=0, row=4)

        self.max_comp = LabelEntry(comp_frame, label_text = "Max compaction(%)",
                                   val_type = float, default_val = 40.,
                                   min_val = 0, max_val = 99)
        self.max_comp.doc = "The compression will stop when this percentage of"
        self.max_comp.doc += " springs will be compacted."
        self.max_comp.grid(column=0, row=5)

        # Display parameters:
        # delta comp
        # scale
        # comp_width
        
        disp_frame = tkinter.Frame(self, relief='ridge', bd = 2)
        disp_frame.grid(column=1, row=1, sticky='NSEW', padx = 3, pady =3)

        comp_label = tkinter.Label(disp_frame, text = "Display parameters",
                                   font = "Helvetica 14 bold", fg = '#009')
        comp_label.grid(column=0, row=0, sticky='N')       

        self.delta_comp = LabelEntry(disp_frame, label_text = "\u0394 comp(%)",
                                     val_type = float, default_val = 3.)
        self.delta_comp.doc = "Percentage of springs to be compacted between "
        self.delta_comp.doc += "two displays."
        self.delta_comp.grid(column=0, row=1)

        self.scale = LabelEntry(disp_frame, label_text = "Scale",
                                val_type = int, default_val = 10)
        self.scale.doc = "Number of pixels per unit of length."
        self.scale.grid(column=0, row=2)

        self.comp_width = LabelEntry(disp_frame, label_text = "Comp width",
                                     val_type = float, default_val = 3)
        self.comp_width.doc = "Width in pixels of a compacted spring "
        self.comp_width.doc += "(will be 1 for a non-compacted spring)."
        self.comp_width.grid(column=0, row=3)                                   

        # Run button
        run_button = tkinter.Button(self, text = "Run", command=self.run,
                                    cursor = "hand2")
        run_button.grid(column=0, row=2)

        # Stop button
        stop_button = tkinter.Button(self, text = "Stop", command=self.stop,
                                     cursor = "hand2")
        stop_button.grid(column=1, row=2) 

    def stop(self):
        self.stopped = True
        

    def run(self):
        '''Fonction executee quand l'utilisateur clique sur "Run".'''
        self.stopped = False
        # Creation de l'echantillon en testant la validite des parametres
        # fournis par l'utilisateur
        try:
            rs = RockSample(self.L.get_val(), self.C.get_val(),
                            self.leq0.get_val(), self.Rl.get_val(),
                            self.A0.get_val(), self.Ka.get_val(),
                            self.E0.get_val(), self.Ke.get_val(),
                            self.F0cr.get_val(), self.D.get_val())
            #rs.debug = True
            print(rs)

            cpr = Compression(rs, self.F0x.get_val(), self.Kbc.get_val(),
                              self.d0.get_val(), self.delt_d.get_val(),
                              self.max_comp.get_val())
            delta_comp_rate = self.delta_comp.get_val()
        except:
            # si une erreur dans les parametres est detectee, soulever
            # l'erreur pour interrompre le programme
            raise

        def draw_sample():
            "fonction d'affichage de l'echantillon"
            DisplayRS(rs, scale = self.scale.get_val(), d = cpr.d)

        iteration = 0
        dFy = DisplayCurve(parent=self, xlegend="\u03B5(%)", ylegend="Fy",
                           yscale = 10000, ymax = 0.05)
  
        cpr.d += cpr.delt_d
        strain = cpr.d / rs.h0 * 100
        comp_rate = rs.comp_count / rs.nsprings * 100
        comp_rate_next_display = 0

        first_compacted_displayed = False

        # Commencer la compression
        while comp_rate < cpr.max_comp:
            if self.stopped:
                print("Stopped.")
                return
            iteration += 1

            cpr.solve()

            test_comp_count = rs.comp_count
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
                cpr.d += cpr.delt_d
                strain = cpr.d / rs.h0 * 100
                print("\tStrain: %f" % strain)

        threading.Thread(target=draw_sample).start()
        time.sleep(2)
        print("Done.")
                
       
if __name__ == '__main__':
    root = ParamGUI()
    root.mainloop()
#TODO
    ## Tester l'echantillon stratifie
    ## Regler le probleme d'encodage dans la barre de titre des fenetres
    ## Trouver pourquoi Fy augmente quand une bande de compaction apparait
    ## Creer une matrice des vecteurs unitaires et la mettre a jour a chaque iteration
