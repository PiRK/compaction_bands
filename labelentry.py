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

class LabelEntry(tkinter.Frame):
    '''Composite widget with a label and an entry.

    Parameters: root window, label text, default min and max entry value,
    the type of value (int, float, str...), label and entry width 
    Methods:
    - get_val: returns the entry value converted into the specified type
    - set_val: changes the entry value
    - set_label_text: changes the label text
    
    '''
    def __init__(self, parent = None, label_text = '', default_val = 1.,
                 min_val = None, max_val = None, val_type = float,
                 relief = "groove", label_width=16, entry_width = 10,
                 help_button = True, doc = '' ):
        tkinter.Frame.__init__(self, parent, relief=relief, bd=2)

        self.parent = parent

        self.min_val = min_val
        self.max_val = max_val
        self.value_type = val_type
        
        if doc == '':
            self.doc = "No documentation available"
        else:
            self.doc = doc
        
        self.value = tkinter.StringVar()
        try:
            self.value.set(val_type(default_val))
        except:
            raise TypeError("Default value %s cannot be " % default_val +
                              "converted into the value type %s." % val_type)
        
        self.label = tkinter.Label(self, text = label_text, width=label_width)
        self.label.grid(column=0,row=0,sticky='E')
        
        self.entry = tkinter.Entry(self, textvariable = self.value, bg='white',
                                   width = entry_width)
        self.entry.grid(column=1,row=0)

        if help_button:
            self.button = tkinter.Button(self, text="?", relief = 'flat',
                                       command = self.show_help, bg = "#EEEEE8",
                                       cursor = "question_arrow")
            self.button.grid(column=2,row=0,sticky='W')

                                     
    def get_val(self):
        '''Return the value in the 'Entry' widget after converting it into
        the correct format (value_type)'''
        val = self.value.get()

        # Try to convert the supplied value into the supplied type
        try:
            val = self.value_type(val)
        except ValueError:
            # if wrong value type entered, change the background color to 
            # red to highlight the problem
            self.entry.configure(bg='red')
            # and raise the error to prevent the program from being run with
            # invalid parameters
            raise 
        if self.min_val is not None and val < self.min_val:
            self.entry.configure(bg='red')
            raise ValueError("Value has to be greater than or equal to %s" %
                             self.min_val)
        elif self.max_val is not None and val > self.max_val:
            self.entry.configure(bg='red')
            raise ValueError("Value needs to be lower than or equal to %s" %
                             self.max_val)
        self.entry.configure(bg='white')
        return  val
            
    def set_val(self, new_value):
        '''Change the value in the Entry field'''
        self.value.set(new_value)

    def set_label_text(self, new_text):
        '''Change the label text'''
        self.label.configure(text = new_text)

    def show_help(self, *args):
        '''Display help'''
        help_win = tkinter.Toplevel(self.parent)
        
        y_scrollbar = tkinter.Scrollbar(help_win, orient = 'vertical')
        y_scrollbar.grid(column = 1, row = 0, sticky='NS')

        help_text = tkinter.Text(help_win, width=60, height=6, wrap = 'word',
                                 yscrollcommand = y_scrollbar.set, bg = '#FFF',
                                 relief = 'flat')
        help_text.grid(column = 0, row = 0)
        help_text.insert('1.0', self.doc)

        y_scrollbar.config(command = help_text.yview)

        t = tkinter.Button(help_win, text = "OK", command = help_win.destroy)
        t.grid(column = 0, row = 1, columnspan = 2)
        
        
# Example of use 
if __name__ == '__main__':
    count = 0
    def testing(*args):
        global count
        count += 1
        print(fra.get_val())
        fra.set_val(fra.get_val() + 1)
        fra.set_label_text("Testing " + str(count))
        
    root = tkinter.Tk()
    fra = LabelEntry(root, label_text = "Testing", val_type = float, default_val = 15, max_val = 55)
    fra.grid(column=0, row=0)



    b = tkinter.Button(root, text="+1", command=testing)
    b.grid(column=0,row=1)

    root.mainloop()
    
