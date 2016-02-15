# compaction_bands
This is a geophysics project I first programmed as a student at the Ecole et Observatoire des Sciences de la Terre. It is based on a scientific paper "Numerical simulation of compaction bands in high-porosity sedimentary rock" by R. Katsman,, E. Aharonov and H. Scher.

Back then I coded it in C which was the only language I knew, and I finished the project in a rush and therefore the code was almost unreadable and impossible to maintain. It was quite frustrating. When I started to learn python, graphical interfaces and object oriented programming, I felt I should rewrite the program in a more readable way. The use of object oriented programming should hopefully make it easier to experiment on different types of compaction thresholds distributions to simulate different kinds of layers in the sandstone without having to rewrite the whole program (just create a class inheriting from the SandstoneSample class and rewrite the method creating the compaction thresholds matrix).

You will require python3 and the latest numpy and scipy libraries (make sure the ones you install work with python3). Unfortunately with some versions of linux (Red Hat and Fedora) I encountered some issues of incomplete libraries causing the necessary scipy function not to work. On other versions of linux - ubuntu - it works just fine but the scipy and numpy libraries were still a bit tricky to install for a geoscientist like me. The easiest way to use the program in my opinion is to install python3.1 on windows and the following two packages:

    http://sourceforge.net/projects/numpy/files/NumPy/1.6.0b2/numpy-1.6.0b2-win32-superpack-python3.1.exe/download
    http://sourceforge.net/projects/scipy/files/scipy/0.9.0/scipy-0.9.0-win32-superpack-python3.1.exe/download


By now you should be able to find windows packages for newer versions of python3. Just make sure to download numpy and scipy with the exact same version number as your version of python3.

With ubuntu, you'll need at least following packages: python3 python3-tk cython3 python3-dev python3-numpy python3-scipy

Maybe there will be more dependencies to install (libblas3gf, libatlas-base-dev ...etc). 
