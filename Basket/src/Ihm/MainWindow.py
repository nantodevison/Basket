# -*- coding: utf-8 -*-
'''
Created on 14 mars 2021

@author: Martin
module de conversion des fichiers .ui en .py
'''

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
import pandas as pd
from Ihm.Initialiser_donnees_IHM import lastDates, nbJourneeImportDefaut
from TeleversementJourneeBdd import JourneeBdd
from datetime import date


class WindowPrincipale(QtWidgets.QMainWindow):
    '''
    la fenetre contenant le QtTablWidget principal
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        super(WindowPrincipale, self).__init__()
        uic.loadUi(r'C:\Users\martin.schoreisz\git\Basket\Basket\src\Ihm\FenetreBaseStat-TTFL.ui', self)
        
        #inititialisation des données de date
        dateMatchAImporter, dateCalendrierAImporter=lastDates()[2:]
        nbJoursMatchs=nbJourneeImportDefaut(dateMatchAImporter)
        self.dateEdit_ImportJournee.setDate(dateMatchAImporter)
        self.dateEdit_Calendrier.setDate(dateCalendrierAImporter)
        self.spinBox_NbjourImport.setValue(nbJoursMatchs)
        
        #signaux slots pour télécharger les données
        self.pushButton_importJournee.clicked.connect(self.televerserJourneeSiteNba)
        #self.pushButton_importJournee.clicked.connect(self.test)
    
    @pyqtSlot()
    def test(self):
        print('test !!')
    
    @pyqtSlot()
    def televerserJourneeSiteNba(self):
        """
        telecharger une ou plusieurs journee du site Nba.com (USA) et les basculer dans la bdd
        in :
            date : string : date de depart de telechargement (YYYY-MM-DD)
            duree : integer : nb de jours a telecharegre a partir de la date de depart
        """
        print('avant fonction Tread')
        self.telecharge=WorkerTelechargement(self.dateEdit_ImportJournee.date().toString('yyyy-MM-dd'),
                                             self.spinBox_NbjourImport.value())
        self.telecharge.start()

class BarreProgression(QtWidgets.QDialog):
    """
    class permettant la génération d'une barre de progression
    """
    
    def __init__(self):
        super(BarreProgression, self).__init__()
        uic.loadUi(r'C:\Users\martin.schoreisz\git\Basket\Basket\src\Ihm\ProgressBar.ui', self)
            
class WorkerTelechargement(QThread):
    """
    class pour executer les actions de telechargement / televersement des donnees
    """
    signalNbMatch=pyqtSignal(int)#envoyer le nb total de la journee en cours
    signalNbJournee=pyqtSignal(int)#envoyer le nb total de journee
    signalNouvelleJournee=pyqtSignal(int)#pour envoyer le numero de la journee telechragee
    
    def __init__(self, date_debut, duree):
        super(WorkerTelechargement, self).__init__()
        self.date_debut=date_debut
        self.duree=duree
        print(self.date_debut,self.duree )
    
    def run(self):
        """
        la fonction de telechargement des donnees
        """
        print('thread run')
        listeDate=[d.strftime('%Y-%m-%d') for d in pd.date_range(start=self.date_debut,
                                                                periods=self.uree)]
        self.signalNbJournee.emit(len(listeDate))
        
        for e,j in  enumerate(listeDate): 
            self.signalNouvelleJournee.emit(e+1)
            print(j)
            journee=JourneeBdd(j)
            self.signalNbMatch.emit(journee.nbMatchs)
            journee.creerAttributsGlobaux()
            #journee.exporterVersBdd()
        
if __name__=="__main__" : 
    import sys 
    app=QtWidgets.QApplication(sys.argv)
    window=WindowPrincipale()
    window.show()
    sys.exit(app.exec_())