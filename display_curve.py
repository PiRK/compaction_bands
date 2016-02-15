#!/usr/bin/env python3
#
# Draw a 2D curve
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

class DisplayCurve(tkinter.Toplevel):
    '''Class for plotting a 2D curve.
    Parameters are:
    the parent window, the width and height of the window, the horizontal and
    vertical scale in pixels per unit, the margin between the plot and the
    window border, the legend on the x and y axis.

    The add_point method plots a line from the previous point to the new one.
    '''
    def __init__(self, parent=None, xmax = 13, ymax = 0.5, xscale = 35,
                 yscale = 500, margin = 20, xlegend='', ylegend=''):
        
        tkinter.Toplevel.__init__(self, parent)

        self.w = 2 * margin + xmax * xscale 
        self.h = 2 * margin + ymax * yscale
        self.xs = xscale
        self.ys = yscale
        self.b = margin

        self.canv = tkinter.Canvas(self, width=self.w, height = self.h, bg = 'white')
        self.canv.pack()

        # y-axis
        self.canv.create_line(margin,self.h - margin, margin, margin,
                              arrow="last")
        self.canv.create_text(margin+5, margin, text=ylegend, anchor="w")
        for y in range(margin, int(self.h - margin), yscale):
            self.canv.create_line(margin - 5, self.h - y, margin + 5, self.h - y)
        
        # y-axis
        self.canv.create_line(margin, self.h - margin, self.w - margin,
                              self.h - margin, arrow="last")
        self.canv.create_text(self.w - margin, self.h - margin - 5,
                              text=xlegend, anchor="se")
        for x in range(margin, self.w - margin - xscale, xscale):
            self.canv.create_line(x, self.h - margin - 5, x, self.h - margin + 5)

        self.prev_x = None
        self.prev_y = None

                
    def add_point(self, x, y):
        x1 = self.b + x * self.xs
        y1 = self.h - self.b - y * self.ys
        if self.prev_x is not None:
            x0 = self.b + self.prev_x * self.xs
            y0 = self.h - self.b - self.prev_y * self.ys
            self.canv.create_line(x0, y0, x1, y1)
        self.prev_x = x
        self.prev_y = y


# Exemple : programme qui affiche un point de la fonction y = 2/x a chaque fois que
# l'utilisateur appui sur un bouton 'Next'
if __name__ == '__main__':
    x = 0.25
    def run(*args):
        global x
        x += 0.25
        y = 2 / x
        
        Fy.add_point(x, y)
        b.configure(text="Next")

    Fy= DisplayCurve(ylegend="Plop", xlegend = "foo", ymax = 4, yscale = 150)
    b = tkinter.Button(Fy, text="First", command = run)
    b.pack()
    Fy.mainloop()
    
    
