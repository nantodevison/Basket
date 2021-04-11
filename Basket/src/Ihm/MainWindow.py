# -*- coding: utf-8 -*-
'''
Created on 14 mars 2021

@author: Martin
module de conversion des fichiers .ui en .py
'''

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSlot
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
        for j in [d.strftime('%Y-%m-%d') for d in pd.date_range(start=self.dateEdit_ImportJournee.date().toString('yyyy-MM-dd'),
                                                                periods=self.spinBox_NbjourImport.value())] : 
            print(j)
            journee=JourneeBdd(j)
            journee.creerAttributsGlobaux()
            journee.exporterVersBdd()
        
if __name__=="__main__" : 
    import sys 
    app=QtWidgets.QApplication(sys.argv)
    window=WindowPrincipale()
    window.show()
    sys.exit(app.exec_())