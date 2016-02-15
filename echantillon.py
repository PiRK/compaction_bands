#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Numerical simulation of compaction bands in sandstone samples
# http://eost.u-strasbg.fr/recherche/renaud/Stages/Knobel/RapportKnobel.pdf
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

import random
import numpy

from math import sqrt, atan, radians, cos

class RockSample:
    '''Un echantillon de gre est modelise par ses dimensions (nombre de lignes
    et de colonnes), le seuil de compaction de ses ressorts F0cr, son desordre
    D, la longueur d'equilibre initiale de ses ressorts leq0,  la reduction de
    la longueur d'equilibre apres compaction Rl=lnew/l0, la constante elastique
    initiale E0 et sa variation apres compaction Ke=Enew/E0.'''

    # Vecteurs unitaires de l'axe des ressorts (l'axe y pointe vers le bas)
    ng = (-1,0)
    nd = (1,0)
    nhg = (-0.5, -sqrt(3)/2)
    nhd = (0.5, -sqrt(3)/2)
    nbg = (-0.5, sqrt(3)/2)
    nbd = (0.5, sqrt(3)/2)
    
    def __init__(self, nlines, ncols, leq0=1, Rl=0.94, A0=1, Ka=1, E0=1, Ke=1,
                F0cr=0.03, D=0):
        self.l = nlines
        self.c = ncols
        self.Rl = Rl
        self.Ke = Ke
        self.Ka = Ka
        self.leq0 = leq0
        self.alpha0 = E0 * A0 / leq0
        # Hauteur initiale
        self.h0 = (nlines - 1) * sqrt(3)/2
        # Seuil de compaction moyen
        self.F0cr = F0cr
        # Desordre
        self.D = D
        # nombre de noeuds sur deux lignes
        self.len2lines = 2*self.c-1
        # nombre de noeuds et de ressorts
        self.n = nlines // 2 * self.len2lines
        self.nsprings = nlines//2*(2*ncols-3)+(nlines-1)*2*(ncols-1)
        # cas d'un nombre de lignes impair :
        if nlines % 2 == 1: 
            self.n += ncols 
            self.nsprings += ncols - 1
        # matrice des seuils de compaction
        self.Fcr = self.compaction_tresholds()
        # Initialisation de la matrice marquant la compaction des ressorts
        self.compacted = []
        for i in range(0, self.n):
            self.compacted.append([False] * self.n)
        # Compteur du nombre de ressorts compactes
        self.comp_count = 0
        # Init du vecteur deplacement des noeuds ; les n premiers elements sont
        # les deplacements selon x, les n suivants les deplacements selon y
        self.u = numpy.array(2 * self.n * [0.])
      
        
    def __repr__(self):
        '''Representation en "ascii-art" de l'echantillon qui s'affichera si
        la fonction print est appelée sur une instance de la classe.
        Par exemple 'print(RockSample(3,3))' affichera
        
        *---*---*
         \ / \ /
          *---*
         / \ / \
        *---*---*
        '''
        representation = ''
        representation += '*---'*(self.c - 1) + '*\n'
        representation += ' \\ /'*(self.c - 1) + '\n'
        representation += '  *'+ '---*'*(self.c - 2) + '\n'
        representation += ' / \\'*(self.c - 1) + '\n'
        representation *= (self.l // 2) 
        # si on a un nombre impair de lignes, rajouter une ligne de noeuds
        if (self.l % 2) == 1:
            representation += '*---'*(self.c - 1) + '*\n'
        # sinon supprimer la derniere ligne de ressorts
        else:
            representation = representation[0:-4*(self.c-1)-1]
        representation += "Desordre : %5f\n" % self.D
        representation += "F0cr : %5f\n" % self.F0cr
        representation += "Ressorts compactes : %d %%\n" % (self.comp_count /
                                                           self.nsprings * 100)
        return representation
        
    def compaction_tresholds(self):
        '''Creation d'une matrice n*n des seuils de compaction avec un seuil
        variant aleatoirement selon une distribution gaussienne de moyenne
        F0cr et d'ecart type F0cr*D.
        La matrice est symetrique car le ressort reliant les noeuds i et j
        peut etre decrit par les couples d'indices (i,j) et (j,i).''' 
        random.seed()
        # Initialisation de tous les elements a 0
        Fcr = []
        for i in range(0, self.n):
            Fcr.append([0.] * self.n)        
        # Remplissage symetrique
        for i in range(0, self.n):
            for j in range(i, self.n):
                Fcr[i][j] = random.gauss(self.F0cr, self.F0cr*self.D)
                Fcr[j][i] = Fcr[i][j]                
        return Fcr

    def test_index_out_of_range(self, index):
        '''Si index >= self.n, renvoie une erreur.'''
        if index >= self.n:
            raise IndexError("Illegal index %d! Index has to be lower"% (index)+
                             " than %d." % (self.n))
        elif index < 0:
            raise IndexError("Illegal negative index (%d)" % index)

    def fg(self,i):
        '''Fonction donnant l'indice du noeud situe a gauche du noeud i'''
        self.test_index_out_of_range(i)
        # Pour les noeuds du bord gauche de l'echantillon, renvoyer 'None'
        if i % self.len2lines == 0 or i % self.len2lines == self.c:
            return None
        else:
            return i - 1

    def fd(self,i):
        '''Fonction donnant l'indice du noeud situe a droite du noeud i'''
        self.test_index_out_of_range(i)
        # Pour les noeuds du bord droit de l'echantillon, renvoyer 'None'
        if i % self.len2lines == self.c-1 or i % self.len2lines == 2*self.c-2:
            return None
        else:
            return i + 1

    def fhg(self,i):
        '''Fonction donnant l'indice du noeud situe en haut a gauche
        du noeud i'''
        self.test_index_out_of_range(i)
        # Pour les noeuds de la premiere ligne ou ceux du bord gauche sur
        # une ligne d'indice pair (0,2...) renvoyer 'None'
        if i < self.c or i % self.len2lines == 0:
            return None
        else:
            return i-self.c

    def fhd(self,i):
        '''Fonction donnant l'indice du noeud situe en haut a gauche
        du noeud i'''
        self.test_index_out_of_range(i)
        # Pour les noeuds de la premiere ligne ou ceux du bord droit sur
        # une ligne d'indice pair renvoyer 'None'
        if i < self.c or i % self.len2lines == self.c-1:
            return None
        else:
            return i - self.c+1
        
    def fbg(self,i):
        '''Fonction donnant l'indice du noeud situe en bas a gauche
        du noeud i'''
        self.test_index_out_of_range(i)
        # Pour les noeuds du bord gauche sur une ligne d'indice pair 
        # renvoyer 'None'
        if i % self.len2lines == 0:
            return None
        # idem pour les noeuds de la derniere ligne si nombre pair de lignes
        elif self.l % 2 == 0 and i > self.n - self.c:
            return None
        # idem pour les noeuds de la derniere ligne si nombre impair de lignes
        elif self.l % 2 == 1 and i >= self.n - self.c:
            return None
        else:
            return i + self.c - 1

    def fbd(self,i):
        '''Fonction donnant l'indice du noeud situe en bas a droite
        du noeud i'''
        self.test_index_out_of_range(i)
        # Pour les noeuds du bord droit sur une ligne d'indice pair renvoyer
        # 'None'
        if i % self.len2lines == self.c - 1:
            return None
        # idem pour les noeuds de la derniere ligne si nombre pair de lignes
        elif self.l % 2 == 0 and i > self.n - self.c:
            return None
        # idem pour les noeuds de la derniere ligne si nombre impair de lignes
        elif self.l % 2 == 1 and i >= self.n - self.c:
            return None
        else:
            return i + self.c
        
    def top_border(self, index):
        '''Renvoie True si l'index est sur la premiere ligne, sinon
        False'''
        self.test_index_out_of_range(index)
        return 0 <= index < self.c

    def bottom_border(self, index):
        '''Renvoie True si l'index est sur la derniere ligne'''
        self.test_index_out_of_range(index)
        # nombre de lignes impair
        if self.l % 2 == 1:
            return self.n - self.c <= index < self.n
        # nombre de lignes pair
        if self.l % 2 == 0 :
            return self.n - self.c < index  < self.n
        
    def right_border(self, index):
        '''Renvoie True si l'index designe un noeud sur le bord droit de
        l'echantillon'''
        self.test_index_out_of_range(index)
        i = index % self.len2lines
        return (i == self.c - 1 or i == self.len2lines - 1)
    
    def left_border(self, index):
        '''Renvoie True si l'index designe un noeud sur le bord gauche de
        l'echantillon'''
        self.test_index_out_of_range(index)
        i = index % self.len2lines
        return (i == 0 or i == self.c)

    def find_compacted(self, Kbc=20):
        '''Fonction qui met a jour le nombre de noeud compactes comp_count et la
        matrice marquant la compaction. Le parametre Kbc represente
        l'augmentation de la raideur sur les bords hauts et bas de l'echantillon
        a cause de la friction entre l'echantillon et la presse.
        '''
        u = self.u
        leq0 = self.leq0
        n = self.n
        
        f = [self.fd, self.fhd, self.fhg]
        n_ = [self.nd, self.nhd, self.nhg]
        for i in range(0, n):
            # Pour chaque noeud, tester 3 ressorts (a droite, en haut a droite
            # et en haut  gauche
            for j in range(0, 3):
                k = f[j](i)
                if (k is not None) and (not self.compacted[i][k]):
                    lreal = sqrt((n_[j][0] * leq0 + u[k] - u[i])**2 +
                                 (n_[j][1] * leq0 + u[k + n] - u[i + n])**2)
                    
                    if (self.top_border(i) or self.bottom_border(i)) and j==0 :
                        # Friction sur les bords
                        alpha = self.alpha0 * Kbc
                    else:
                        alpha = self.alpha0
                    if -alpha * (lreal - leq0) > self.Fcr[i][k]:
                        self.compacted[i][k] = True
                        self.compacted[k][i] = True
                        self.comp_count += 1


class StratifiedRockSample(RockSample):
    '''Echantillon stratifie.
    Identique a un echantillon normal sauf pour la distribution des
    seuils de compaction. L'echantillon est compose de deux types de strates
    definies par leur epaisseur t0 et t1, leur pendage et leur seuils de
    compaction F0cr et F1cr.'''

    def __init__(self, nlines, ncols, leq0=1, Rl=0.94, A0=1, Ka=1, E0=1, Ke=1,
                 F0cr=0.028, D=0, F1cr=0.032, dip = 0, t0 = 15, t1 = 15):

        self.F1cr = F1cr
        # pendage en degres
        self.dip = dip
        # epaisseur de la couche de seuil  F0cr
        self.thickness0 = t0
        # epaisseur de la couche de seuil  F1cr
        self.thickness1 = t1
        if t0 < 0 or t1 < 0:
            raise ValueError("Layer thickness cannot be a negative value")
        # RockSample.__init__(nlines, ncols, leq0, Rl, A0, Ka, E0, Ke, F0cr, D)
        RockSample.__init__(self, nlines, ncols, leq0, Rl, A0, Ka, E0, Ke, F0cr, D)



    def y_coord(self, i):
        '''Returns the y coordinate of node indexed by i'''
        y = i // self.len2lines * 2 + (i % self.len2lines) // self.c
        y *= sqrt(3) / 2 * self.leq0
        return y
    
    def x_coord(self, i):
        '''Returns the x coordinate of node indexed by i'''
        x = (i % self.len2lines)
        # If node is on a "long" line
        if x < self.c:
            x = x * self.leq0
        # If node is on an odd line
        else:
            x = (x - self.c + 0.5) * self.leq0
        return x


    def which_layer(self, index):
        '''Determine dans quelle strate (0 ou 1) le noeud se trouve.'''

        self.test_index_out_of_range(index)

        def f(x, y):
            '''Projection orthogonale du point (x, y) sur un axe y'
            perpendiculaire a la stratification.'''
            if y > 0.00001 or y < -0.00001:
                return sqrt(x**2 + y**2) * cos(radians(self.dip) + atan(x / y))
            else:
                return sqrt(x**2 + y**2) * cos(radians(self.dip) + radians(90))

        proj = f(self.x_coord(index), self.y_coord(index))
        
        dummy = 0
        if proj > 0:
            while dummy < proj:
                dummy += self.thickness0
                if dummy >= proj:
                    return 0
                dummy += self.thickness1
                if dummy >= proj:
                    return 1
        elif proj < 0:
            while dummy > proj:
                dummy -= self.thickness1
                if dummy < proj:
                    return 1
                dummy -= self.thickness0
                if dummy < proj:
                    return 0
            return 0
    
    def compaction_tresholds(self):
        '''Matrice des seuils de compactions'''
        random.seed()
        # Initialisation de tous les elements a 0
        Fcr = []
        for i in range(0, self.n):
            Fcr.append([0.] * self.n)
        for i in range(0, self.n):
            layer = self.which_layer(i)
            for j in range(i, self.n):
                if layer == 0:
                    Fcr[i][j] = random.gauss(self.F0cr,self.F0cr*self.D)
                elif layer == 1:
                    Fcr[i][j] = random.gauss(self.F1cr,self.F1cr*self.D)
                Fcr[j][i] = Fcr[i][j]
        return Fcr


 
