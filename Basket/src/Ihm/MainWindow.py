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
from TelechargementDonnees import Calendrier
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
        dateMatchAImporter, dateCalendrierAImporter, idSaisonRecent=lastDates()[2:]
        nbJoursMatchs=nbJourneeImportDefaut(dateMatchAImporter)
        self.dateEdit_ImportJournee.setDate(dateMatchAImporter)
        self.dateEdit_Calendrier.setDate(dateCalendrierAImporter)
        self.spinBox_NbjourImport.setValue(nbJoursMatchs)
        self.spinBox_idSaisonCalendrier.setValue(idSaisonRecent)
        
        
        #signaux slots pour télécharger les données
        self.pushButton_importJournee.clicked.connect(self.televerserJourneeSiteNba)
        self.pushButton_importCalendrier.clicked.connect(self.transfertCalendrier)
    
    @pyqtSlot()    
    def transfertCalendrier(self):
        """
        transferer le calendrier telecharge grace a la classe calendrier() dans la bdd
        in :
            id_saison : integer, identiiant saioson
            date_depart : string format YYYY-MM-DD
            duree : integer :nb de jours apres date de depart
            bdd : id de connxion a la bdd
        """
        try : 
            self.threadCalendrier = QThread()
            print('avant creation worker')
            print(self.dateEdit_Calendrier.date().toString('yyyy-MM-dd'))
            self.workerCalendrier=WorkerCalendrier(self.spinBox_idSaisonCalendrier.value(), 
                                                   self.dateEdit_Calendrier.date().toString('yyyy-MM-dd'), 
                                                   self.spinBox_calendrierNbJourImport.value())
            print('avant move to')
            self.workerCalendrier.moveToThread(self.threadCalendrier)
            print('avant signaux/slots')
            self.threadCalendrier.started.connect(self.workerCalendrier.run)
            self.workerCalendrier.finished.connect(self.threadCalendrier.quit)
            self.workerCalendrier.finished.connect(self.workerCalendrier.deleteLater)
            self.workerCalendrier.finished.connect(self.fermerPgBar)
            self.threadCalendrier.finished.connect(self.threadCalendrier.deleteLater)
            self.barresProgressCalendrier=BarreProgression(barreEtape=False)
            print('postbar')
            self.workerCalendrier.signalJourneeFaite.connect(self.setJourneeDone)
            self.workerCalendrier.signalNbJournee.connect(self.initPgBarNouvelleJournee)
            print('avant start')
            self.threadCalendrier.start()
        except Exception as e : 
            print(e)

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
        self.threadTelechargement = QThread()
        #creer le worker
        print('avant creation worker')
        self.workerTelechargement=WorkerTelechargement(self.dateEdit_ImportJournee.date().toString('yyyy-MM-dd'),
                                             self.spinBox_NbjourImport.value())
        #envoyer le worker dans le thread
        print('avant move to')
        self.workerTelechargement.moveToThread(self.threadTelechargement)
        #signaux/slots
        print('avant signaux/slots')
        self.threadTelechargement.started.connect(self.workerTelechargement.run)
        self.workerTelechargement.finished.connect(self.threadTelechargement.quit)
        self.workerTelechargement.finished.connect(self.workerTelechargement.deleteLater)
        self.workerTelechargement.finished.connect(self.fermerPgBar)
        self.threadTelechargement.finished.connect(self.threadTelechargement.deleteLater)
        self.barresProgressTelechargement=BarreProgression()
        self.workerTelechargement.signalNbJournee.connect(self.initPgBarNouvelleJournee)
        self.workerTelechargement.signalNouvelleJournee.connect(self.setPgBarNouvelleJournee)
        self.workerTelechargement.signalNbMatch.connect(self.setPgBarNbMatchs)
        self.workerTelechargement.signalAvancement.connect(self.setTextMatchEnCour)
        self.workerTelechargement.signalJourneeDone.connect(self.setJourneeDone)
        self.workerTelechargement.signalMatchFait.connect(self.setPgBarMatchFait)
        
        # Start the thread
        self.threadTelechargement.start()
    
    @pyqtSlot(int)
    def setPgBarNbMatchs(self,nbMatchs):
        self.barresProgressTelechargement.progressBar_etape.setMaximum(nbMatchs)
        self.barresProgressTelechargement.progressBar_etape.setValue(1)
    
    @pyqtSlot(str)
    def setTextMatchEnCour(self,nomMatch):
        self.barresProgressTelechargement.label_etape.setText(nomMatch)
    
    @pyqtSlot(int)
    def setPgBarMatchFait(self, numMatch):
        self.barresProgressTelechargement.progressBar_etape.setValue(numMatch)
    
    @pyqtSlot(int)    
    def initPgBarNouvelleJournee(self,nbJournee):
        if self.sender()==self.workerTelechargement :
            self.barresProgressTelechargement.progressBar_nbJournee.setMaximum(nbJournee)
        elif self.sender()==self.workerCalendrier :
            self.barresProgressCalendrier.progressBar_nbJournee.setMaximum(nbJournee)
            
    @pyqtSlot(int)   
    def setPgBarNouvelleJournee(self, numJournee): 
        if self.sender()==self.workerTelechargement :
            self.barresProgressTelechargement.label_etape.setText('Import des blessures et nombre de matchs...')       
            self.barresProgressTelechargement.label_nbJournee.setText(f'Traitement de la journée {numJournee}')
            
    @pyqtSlot(int)    
    def setJourneeDone(self, numJournee):
        print()
        if self.sender()==self.workerTelechargement :
            self.barresProgressTelechargement.progressBar_nbJournee.setValue(numJournee)
        elif self.sender()==self.workerCalendrier :
            self.barresProgressCalendrier.progressBar_nbJournee.setValue(numJournee)
            self.barresProgressCalendrier.label_nbJournee.setText(f'Traitement de la journée {numJournee+1}')
            
    @pyqtSlot()
    def fermerPgBar(self):
        if self.sender()==self.workerTelechargement :
            self.barresProgressTelechargement.close()
        elif self.sender()==self.workerCalendrier :
            self.barresProgressCalendrier.close()

class BarreProgression(QtWidgets.QDialog):
    """
    class permettant la génération d'une barre de progression
    """
    
    def __init__(self, barreJournee=True, barreEtape=True):
        super(BarreProgression, self).__init__()
        uic.loadUi(r'C:\Users\martin.schoreisz\git\Basket\Basket\src\Ihm\ProgressBar.ui', self)
        print('uiChargee')
        self.progressBar_etape.setMinimum(0)
        self.progressBar_etape.setValue(0)
        self.progressBar_nbJournee.setMinimum(0)
        self.progressBar_nbJournee.setValue(0)
        self.label_etape.setText('Initialisation...')
        self.label_nbJournee.setText('Initialisation...')
        print('avantShow')
        self.show()
        if not barreEtape : 
            self.progressBar_etape.hide()
        self.WA_DeleteOnClose=True
        
            
class WorkerTelechargement(QObject):
    """
    class pour executer les actions de telechargement / televersement des donnees de Matchs joues
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
            self.signalNbJournee.emit(self.duree)
            print('avant boucle')
            for e,j in  enumerate([d.strftime('%Y-%m-%d') for d in pd.date_range(start=self.date_debut,
                                                                    periods=self.duree)]): 
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
        
class WorkerCalendrier(QObject):
    """
    class pour executer les actions de telechargement / televersement du calendrier
    """
    finished = pyqtSignal()
    signalJourneeFaite = pyqtSignal(int)
    signalNbJournee=pyqtSignal(int)
    
    def __init__(self, idSaison, dateDepart, duree):
        super(WorkerCalendrier, self).__init__()
        self.idSaison=idSaison
        self.dateDepart=dateDepart
        self.duree=duree
            
    def run(self):
        print('debut run')
        try : 
            self.signalNbJournee.emit(self.duree)
            cal=Calendrier(self.idSaison,self.dateDepart,self.duree)
            print('avant tranbsmission')
            #cal.signalJourneeFaite.connect(self.transmissionjourneeFaite)
            print('avant calendrier')
            cal.telechargerCalendrier()
            cal.exporterVersBdd()
            #self.finished.emit()
        except Exception as e : 
            print(e)
        
    @pyqtSlot(int)
    def transmissionjourneeFaite(self, numjournee):
        self.signalJourneeFaite.emit(numjournee)
        
if __name__=="__main__" : 
    import sys 
    app=QtWidgets.QApplication(sys.argv)
    window=WindowPrincipale()
    window.show()
    sys.exit(app.exec_())