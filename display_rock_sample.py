#!/usr/bin/env python3
#
# Draw the rock sample in a separate graphical  window
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
from math import sqrt

class DisplayRS(tkinter.Toplevel):
    '''Class for drawing a rock sample in a separate window.
    Parameters are:
    the parent window, the rock sample, the scale (pixels per unit of distance),
    the displacement, the margin between the plot and the window border.
    
    The add_point method plots a line from the previous point to the new one.
    '''
    nd = (1,0)
    # In a tkinter canvas the origin is in the top left corner and the y
    # coordinate increases downwards
    nbd = (0.5,sqrt(3)/2)
    nbg = (-0.5,sqrt(3)/2)

    def __init__(self, rs, parent=None, scale = 10, d = None,
                 margin = 30, spring_width = 1, compacted_spring_width = 3):
        
        tkinter.Toplevel.__init__(self, parent)

        self.s = scale
        self.m = margin
        
        self.sw = spring_width
        self.csw = compacted_spring_width

        self.rs = rs
        
        # Displacement
        self.d = d
        
        # Canvas width
        self.w = 2 * margin + (rs.c - 1) * scale
        # Canvas height
        self.h = 2 * margin + (rs.l - 1) * scale * sqrt(3.) / 2

        self.ymax = (rs.l - 1) * scale * sqrt(3./2)

        # Canvas
        self.canv = tkinter.Canvas(self, width=self.w, height = self.h, bg = 'white')
        self.canv.pack()

        self.draw()

        # Labels (strain and compaction rate)
        if d is not None:
            ltext = "\u03b5 = %.3f%%" % (self.d / self.rs.h0 * 100)
            self.label_eps = tkinter.Label(self, text = ltext)
            self.label_eps.pack()
        ltext = "Compaction rate: %.3f%%" % (self.rs.comp_count /
                                             self.rs.nsprings *100)
        self.label_comp = tkinter.Label(self, text = ltext)
        self.label_comp.pack()

##        # Put the strain value in the window title (PROBLEME D'ENCODAGE DES
##        # CARACTERES GRECS (epsilon) A REGLER !!!!!!!!!!!!!!!!!!!!!!!!!!!!!  
##        if d is not None:
##            titre = "\u03b5 = %.1f%%" % (self.d / self.rs.h0 * 100)
##            self.title(titre)
        self.mainloop()

    def y_coord(self, i):
        '''Returns the y coordinate of node indexed by i'''
        y = i // self.rs.len2lines * 2 + (i % self.rs.len2lines) // self.rs.c
        y *= sqrt(3)/2 * self.rs.leq0
        return y
    
    def x_coord(self, i):
        '''Returns the x coordinate of node indexed by i'''
        x = (i % self.rs.len2lines)
        # If node is on a "long" line
        if x < self.rs.c:
            x = x * self.rs.leq0
        # If node is on an odd line
        else:
            x = (x - self.rs.c + 0.5) * self.rs.leq0
        return x
    
    def draw(self):
        '''For each node in the spring network, draw the right, the bottom-right
        and the left spring
        '''
        for i in range(0, self.rs.n):
            x0 = self.m + self.s * (self.x_coord(i) + self.rs.u[i])
            y0 = self.m + self.s * (self.y_coord(i) + self.rs.u[i+self.rs.n]) 
            # ressort a droite, en bas a droite, en bas a gauche
            kd, kbd, kbg = (self.rs.fd(i), self.rs.fbd(i), self.rs.fbg(i))
            for k in (kd, kbd, kbg):
                if k is not None:
                    if not self.rs.compacted[i][k]:
                        sw = self.sw
                    else:
                        sw = self.csw
                    x1 = self.m + self.s * (self.x_coord(k) + self.rs.u[k])
                    y1 = self.m + self.s * (self.y_coord(k) + 
                                            self.rs.u[k+self.rs.n])
                    self.canv.create_line(x0, y0, x1, y1, width = sw)
            
        


# Exemple : dessin d'un echantillon de taille 23x15
if __name__ == '__main__':
    from echantillon import RockSample

    a = RockSample(23, 15)
    
    DisplayRS(a, d = 1)


            
