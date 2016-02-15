
from math import sqrt
import numpy
import scipy.sparse
#from scipy.sparse.linalg import spsolve
from numpy.linalg import solve

from echantillon import RockSample, StratifiedRockSample

#TEST
from  display_curve import DisplayCurve
from display_rock_sample import DisplayRS
from tkinter import *
import threading

class Compression:
    '''On definit l'experience de compression par son echantillon de gre rs, la
    force de confinement horizontale F0x, le rapport d'augmentation de la 
    raideur des ressorts par friction Kbc et l'intervalle de deformation 
    applique a chaque etape de l'experience delta_d.'''
    
    # Vecteurs unitaires de l'axe des ressorts (l'axe y point vers le bas)
    ng = (-1, 0)
    nd = (1, 0)
    nhg = (-0.5, -sqrt(3)/2)
    nhd = (0.5, -sqrt(3)/2)
    nbg = (-0.5, sqrt(3)/2)
    nbd = (0.5, sqrt(3)/2)
    
    def __init__(self, rs, F0x=0, Kbc=20, d0 = 0., delta_d=0.005, max_comp=40):
        # echantillon de gre
        self.rs = rs
        # force horizontale de confinement
        self.F0x = F0x
        # force verticale moyenne appliquee sur l'echantillon
        self.Fy = 0
        # rapport d'augmentation de la raideur des ressorts a cause de la
        # friction sur la 1ere et derniere ligne de l'echantillon
        self.Kbc = Kbc
        # deplacement applique sur la 1ere et derniere ligne de l'echantillon
        # a chaque etape de l'experience
        self.delt_d = delta_d
        # deplacement cumule
        self.d = d0
        # pourcentage maximal de ressorts compactes (utilisé comme condition
        # pour terminer l'experience)
        self.max_comp = max_comp

        # Resolution du systeme pour l'etat initial (d=0, F0x)
        self.solve()


    def build_matrix(self):
        '''Remplissage de la matrice A du systeme F = A u''' 
        # Fonctions donnant l'indice d'un noeud adjacent au noeud i 
        f = [self.rs.fg, self.rs.fd, self.rs.fhg, self.rs.fhd, self.rs.fbd,
             self.rs.fbg]
        # Vecteurs unitaires entre deux noeuds adjacents
        n_ = [self.ng, self.nd, self.nhg, self.nhd, self.nbd, self.nbg]
        # Nombre de noeuds dans l'echantillon
        n = self.rs.n

        # Initialisation de A en tant que "List of lists matrix" 
        self.A = scipy.sparse.lil_matrix((2*n, 2*n))

        # Boucle sur tous les noeuds
        for i in range(0, n):
            # Premiere ligne
            if self.rs.top_border(i):
                # uy = -d
                self.A[i + n, i + n] = 1
                for j in range(0, 6):
                    k = f[j](i)
                    if k is not None:
                        if not self.rs.compacted[i][k]:
                            alpha= self.rs.alpha0 * self.Kbc
                        else:
                            alpha = self.rs.alpha0 * self.Kbc * self.rs.Ke
                            alpha *= self.rs.Ka / self.rs.Rl
                        
                        self.A[i, k] = alpha * n_[j][0]**2
                        self.A[i, k + n] = alpha * n_[j][0] * n_[j][1]

                        self.A[i, i] += -alpha * n_[j][0]**2
                        self.A[i, i + n] += -alpha * n_[j][1] * n_[j][0] 
                                                
            # Derniere ligne
            elif self.rs.bottom_border(i):
                # uy = 0
                self.A[i + n, i + n] = 1
                for j in range(0, 6):
                    k = f[j](i)
                    if k is not None:
                        if not self.rs.compacted[i][k]:
                            alpha= self.rs.alpha0 * self.Kbc
                        else:
                            alpha= self.rs.alpha0*self.Kbc*self.rs.Ke*self.rs.Ka/self.rs.Rl
                        
                        self.A[i, k] = alpha * n_[j][0]**2
                        self.A[i, k + n] = alpha * n_[j][0] * n_[j][1]

                        self.A[i, i] += -alpha * n_[j][0]**2
                        self.A[i, i + n] += -alpha * n_[j][1] * n_[j][0]
            # Toutes les autres lignes
            else:
                for j in range(0, 6):
                    k = f[j](i)
                    if k is not None:
                        if not self.rs.compacted[i][k]:
                            alpha = self.rs.alpha0
                        else:
                            alpha = self.rs.alpha0*self.rs.Ke*self.rs.Ka/self.rs.Rl
                        
                        self.A[i, k] = alpha * n_[j][0]**2
                        self.A[i + n, k] = alpha * n_[j][1] * n_[j][0]
                        self.A[i, k + n] = alpha * n_[j][0] * n_[j][1]
                        self.A[i + n, k + n] = alpha * n_[j][1]**2
                        
                        self.A[i, i] += -alpha * n_[j][0]**2
                        self.A[i, i + n] += -alpha * n_[j][0] * n_[j][1] 
                        self.A[i + n, i] += -alpha * n_[j][1] * n_[j][0]
                        self.A[i + n, i + n] += -alpha * n_[j][1]**2
        # Convert A to Compressed Sparse Row format
        self.A = self.A.tocsr()

    def build_F(self):
        '''Remplissage de la matrice F du systeme F = A u'''
        f = [self.rs.fg, self.rs.fd, self.rs.fhg, self.rs.fhd, self.rs.fbd,
             self.rs.fbg]
        n_ = [self.ng, self.nd, self.nhg, self.nhd, self.nbd, self.nbg]
        
        n = self.rs.n
        leq0 = self.rs.leq0
        Rl = self.rs.Rl
        
        # Initialisation a 0       
        self.F = numpy.array(2 * n * [0.])

        # Boucle sur tous les noeuds
        for i in range(0, n):
            # Force de confinement horizontale
            if self.rs.left_border(i):
                self.F[i] += self.F0x
            elif self.rs.right_border(i):
                self.F[i] -= self.F0x
                
            # Premiere ligne
            if self.rs.top_border(i):
                alpha= self.rs.alpha0 * self.Kbc * self.rs.Ke * self.rs.Ka / Rl
                # uy = d/2
                self.F[i + n] = self.d / 2
                for j in range(0,6):
                    k = f[j](i)
                    if (k is not None) and self.rs.compacted[i][k]:
                       self.F[i] += -alpha * leq0 * (1 - Rl) * n_[j][0]
                       
            # Derniere ligne
            elif self.rs.bottom_border(i):
                alpha= self.rs.alpha0 * self.Kbc * self.rs.Ke * self.rs.Ka / Rl
                # uy = d/2
                self.F[i + n] = -self.d / 2
                for j in range(0,6):
                    k = f[j](i)
                    if (k is not None) and self.rs.compacted[i][k]:
                       self.F[i] += -alpha * leq0 * (1 - Rl) * n_[j][0]
            else:
                alpha = self.rs.alpha0 * self.rs.Ke * self.rs.Ka / Rl
                for j in range(0,6):
                    k = f[j](i)
                    if (k is not None) and self.rs.compacted[i][k]:
                       self.F[i]   += -alpha * leq0 * (1 - Rl) * n_[j][0]
                       self.F[i+n] += -alpha * leq0 * (1 - Rl) * n_[j][1]


    def vertical_force_applied(self):  
        '''Calcul de la force verticale moyenne appliquee sur l'echantillon'''
        Fy = 0
        count = 0

        f = [self.rs.fhd, self.rs.fhg, self.rs.fbd, self.rs.fbg]
        n_ = [self.nhd, self.nhg, self.nbd, self.nbg]
        u = self.rs.u
        n = self.rs.n
        
        for i in range(0, self.rs.n):
            if self.rs.bottom_border(i):
                Fyi = 0
                # rangee du bas : Fy depend des ressorts hg et hd 
                for j in range(0, 2):
                    k = f[j](i)
                    if k is None: continue
                    if not self.rs.compacted[i][k]:
                        alpha = self.rs.alpha0
                        Fyi += alpha*((u[k]-u[i])*n_[j][0] + (u[k+n]-u[i+n])*n_[j][1])
                    else:
                        alpha = self.rs.alpha0*self.rs.Ke*self.rs.Ka/self.rs.Rl
                        Fyi += alpha*((u[k]-u[i])*n_[j][0] + (u[k+n]-u[i+n])*n_[j][1] +
                                      self.rs.leq0 * (1 - self.rs.Rl))
                    Fyi *= n_[j][1]
                        
                Fy += abs(Fyi)
                count += 1
            if self.rs.top_border(i):
                Fyi = 0
                # rangee du haut : Fy depend des ressorts bg et bd 
                for j in range(2, 4):
                    k = f[j](i)
                    if k is None: continue
                    if not self.rs.compacted[i][k]:
                        alpha = self.rs.alpha0
                        Fyi += alpha*((u[k]-u[i])*n_[j][0] + (u[k+n]-u[i+n])*n_[j][1])
                    else:
                        alpha = self.rs.alpha0*self.rs.Ke*self.rs.Ka/self.rs.Rl
                        Fyi += alpha*((u[k]-u[i])*n_[j][0] + (u[k+n]-u[i+n])*n_[j][1] +
                                      self.rs.leq0 * (1 - self.rs.Rl))
                    Fyi *= n_[j][1]
                    
                Fy += abs(Fyi)
                count += 1
        # moyenne des forces verticales s'appliquant sur tous les noeuds du haut
        # et du bas de l'echantillon
        self.Fy = Fy / count

    def solve(self):
        '''Resolution du systeme matriciel self.F = self.A self.rs.u'''
        self.build_matrix()
        self.build_F()

        #self.rs.u = spsolve(self.A, self.F)
        self.rs.u = solve(self.A.todense(), self.F)

        self.vertical_force_applied()
        self.rs.find_compacted()




# Test               
if __name__ == '__main__':
    

    def mainloop(*args):
        '''Compression de l'echantillon.'''
        iteration = 0
        a = RockSample(23, 15, D=0.02)
        print("Echantillon initial :")
        print(a)
        b = Compression(a, delta_d = -0.005)


        dfy = DisplayFy(r,xlegend="\u03B5(%)", ylegend="Fy")
                    
        # Boucle principale: compression tant que max comp % des ressorts ne 
        # sont pas compactes.
        while b.rs.comp_count < b.max_comp / 100 * b.rs.nsprings and b.Fy < 1:
            test_comp_count = b.rs.comp_count        
            b.solve()
            print(b.rs.comp_count )
            # si pas de nouveaux ressorts compactes, incrementer la compression
            if b.rs.comp_count == test_comp_count:
                strain = -b.d / b.rs.h0 * 100
                compaction_rate = b.rs.comp_count / b.rs.nsprings * 100
                print("Iteration %5d: " % iteration)
                print("\tTaux de compression %f" % strain)
                print("\tTaux de compaction %f" % compaction_rate)
                print("\tForce applique %f" % b.Fy)
                dfy.add_point(strain, b.Fy)
                b.d += b.delt_d
                
            iteration += 1

            def dummy():
                DisplayRS(b.rs, scale = 30)

            if iteration % 50 == 1  or 17 < iteration < 47:
                threading.Thread(target=dummy).start()
                
 
    r=Tk()
    Button(r,text="x",command=mainloop).pack()
    r.mainloop()
   
