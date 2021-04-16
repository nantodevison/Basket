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
from PyQt5.QtCore import QObject
from time import sleep


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
        print('avant ouverture Tread')
        #ouvrir le thread
        self.thread = QThread()
        #creer le worker
        print('avant creation worker')
        self.workerTelechargement=WorkerTelechargement(self.dateEdit_ImportJournee.date().toString('yyyy-MM-dd'),
                                             self.spinBox_NbjourImport.value())
        #envoyer le worker dans le thread
        print('avant move to')
        self.workerTelechargement.moveToThread(self.thread)
        #signaux/slots
        print('avant signaux/slots')
        self.thread.started.connect(self.workerTelechargement.run)
        self.workerTelechargement.finished.connect(self.thread.quit)
        self.workerTelechargement.finished.connect(self.workerTelechargement.deleteLater)
        self.workerTelechargement.finished.connect(self.fermerPgBar)
        self.thread.finished.connect(self.thread.deleteLater)
        self.barresProgress=BarreProgression()
        self.workerTelechargement.signalNbJournee.connect(self.initPgBarNouvelleJournee)
        self.workerTelechargement.signalNouvelleJournee.connect(self.setPgBarNouvelleJournee)
        self.workerTelechargement.signalNbMatch.connect(self.setPgBarNbMatchs)
        self.workerTelechargement.signalAvancement.connect(self.setTextMatchEnCour)
        self.workerTelechargement.signalJourneeDone.connect(self.setJourneeDone)
        self.workerTelechargement.signalMatchFait.connect(self.setPgBarMatchFait)
        
        # Start the thread
        self.thread.start()
    
    @pyqtSlot(int)
    def setPgBarNbMatchs(self,nbMatchs):
        self.barresProgress.progressBar_etape.setMaximum(nbMatchs)
        self.barresProgress.progressBar_etape.setValue(1)
    
    @pyqtSlot(str)
    def setTextMatchEnCour(self,nomMatch):
        self.barresProgress.label_etape.setText(nomMatch)
    
    @pyqtSlot(int)
    def setPgBarMatchFait(self, numMatch):
        self.barresProgress.progressBar_etape.setValue(numMatch)
    
    @pyqtSlot(int)    
    def initPgBarNouvelleJournee(self,nbJournee):
        self.barresProgress.progressBar_nbJournee.setMaximum(nbJournee)
    
    @pyqtSlot(int)   
    def setPgBarNouvelleJournee(self, numJournee): 
        #self.barresProgress.progressBar_etape.setValue(1)
        self.barresProgress.label_etape.setText('Import des blessures et nombre de matchs...')       
        self.barresProgress.label_nbJournee.setText(f'Traitement de la journée {numJournee}')
        
    @pyqtSlot(int)    
    def setJourneeDone(self, numJournee):
        self.barresProgress.progressBar_nbJournee.setValue(numJournee)
    
    @pyqtSlot()
    def fermerPgBar(self):
        self.barresProgress.close()

class BarreProgression(QtWidgets.QDialog):
    """
    class permettant la génération d'une barre de progression
    """
    
    def __init__(self):
        super(BarreProgression, self).__init__()
        uic.loadUi(r'C:\Users\martin.schoreisz\git\Basket\Basket\src\Ihm\ProgressBar.ui', self)
        self.progressBar_etape.setMinimum(0)
        self.progressBar_etape.setValue(0)
        self.progressBar_nbJournee.setValue(0)
        self.label_etape.setText('Initialisation...')
        self.label_nbJournee.setText('Initialisation...')
        self.show()
        self.WA_DeleteOnClose=True
        
            
class WorkerTelechargement(QObject):
    """
    class pour executer les actions de telechargement / televersement des donnees
    """
    finished = pyqtSignal()
    signalJourneeDone=pyqtSignal(int)
    signalNbMatch=pyqtSignal(int)#envoyer le nb total de la journee en cours
    signalNbJournee=pyqtSignal(int)#envoyer le nb total de journee
    signalNouvelleJournee=pyqtSignal(int)#pour envoyer le numero de la journee telechragee
    signalAvancement=pyqtSignal(str)#pour trabsmettre le signal issu de l'objet journee
    signalMatchFait=pyqtSignal(int)#marquer match fait
    
    def __init__(self, date_debut, duree):
        super(WorkerTelechargement,self).__init__()
        self.date_debut=date_debut
        self.duree=duree
        print(self.date_debut,self.duree )
    
    def run(self):
        print('thread run')
        try :
            listeDate=[d.strftime('%Y-%m-%d') for d in pd.date_range(start=self.date_debut,
                                                                    periods=self.duree)]
            print(listeDate)
            self.signalNbJournee.emit(len(listeDate))
            print('avant boucle')
        
            for e,j in  enumerate(listeDate): 
                self.signalNouvelleJournee.emit(e+1)
                print(j)
                journee=JourneeBdd(j)
                self.signalNbMatch.emit(journee.nbMatchs+1)
                journee.signalAvancement.connect(self.transmissionDonneesJournee)
                journee.signalMatchFait.connect(self.transmissionMatchFait) 
                print(f'journee cree, nb matchs : {journee.nbMatchs}')
                journee.creerAttributsGlobaux()  
                self.signalJourneeDone.emit(e+1)
                print('fait')     
                journee.exporterVersBdd()
                
        except Exception as e : 
            print(e)
        print('avant finished')
        self.finished.emit()
    
    @pyqtSlot(str)
    def transmissionDonneesJournee(self, nomMatch):
        self.signalAvancement.emit(nomMatch)
    
    @pyqtSlot(int)
    def transmissionMatchFait(self, numMatch):
        self.signalMatchFait.emit(numMatch)
        
if __name__=="__main__" : 
    import sys 
    app=QtWidgets.QApplication(sys.argv)
    window=WindowPrincipale()
    window.show()
    sys.exit(app.exec_())