# -*- coding: utf-8 -*-
'''
Created on 29 déc. 2020

@author: martin.schoreisz
Module de telechragement des donnees depuis le site français de la nba
'''

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException,TimeoutException
import time, os
import pandas as pd
import numpy as np

urlSiteNbaScore='https://fr.global.nba.com/scores/'
nomsColonnesStat=['nom', 'nom.1', 'position', 'minute', 'points', 'rebonds', 'passes_dec', 'steal', 
 'contres', 'tir_reussi', 'tir_tentes', 'pct_tir', 'trois_pt_r', 'trois_pt_t', 'pct_3_pt', 
 'lanc_frc_r', 'lanc_frc_t', 'pct_lfrc', 'rebonds_o', 'rebonds_d', 'ball_perdu', 'faute_p', 
 'plus_moins']
nomsColonnesMatch=['equipe','q1','q2','q3','q4','final']
dnpTupleTexte=("Pas en tenue","N'a pas joué")

def CreationDriverFirefox():
    """
    ouvrir un driver Selenium
    """
    driver = webdriver.Firefox()
    driver.implicitly_wait(20)
    time.sleep(5)
    return driver

class JourneeSiteNba(object):
    '''
    Resultats des matchs publies sur le site pour une date
    '''

    def __init__(self, dateJournee, sourceDonnees='internet',dossierExportCsv=r'C:\Users\martin.schoreisz\Documents\AffairesEnCours\temp\basket'):
        '''
        Attributes
            dateJournee : string au format YYYY-MM-DD
            urlDateJournee : string : url de la date de la journee
            sourceDonnees : string : soure de la donnees : "internet" ou "csv" si la donnees a ete precedemment chargees depuis le site
            driver : selenium driver firefox, uniquement si sourceDonnees='internet'
            dossierDate : si on enregistre des csv (uniquement si sourceDonnees='internet') : dossier qui conteint les donnees de la journee
            dicoJournee : dico avec en cle un integer  et en value un dico de 3 clé : match, stats_eO et stat_e1 qui contein les dfs de donnees
            dossierExportCsv : dossier pour export de la journee telechargee
        '''
        self.dateJournee=dateJournee
        self.urlDateJournee=fr'{urlSiteNbaScore}#!/{self.dateJournee}'
        self.sourceDonnees=sourceDonnees
        self.dossierExportCsv=dossierExportCsv
        if self.sourceDonnees=='internet' : 
            self.driver=CreationDriverFirefox()
            self.dossierDate=os.path.join(self.dossierExportCsv,self.dateJournee)
        self.dicoJournee=self.dicoMatchs()
        
    def __str__(self):
        return '\n'.join([f'match {i} \n'+ v['match'].to_string(columns=['equipe', 'final'], index=False,
                    header=False) for i,v in enumerate(self.dicoJournee.values())])
    
    
    def getListFeuilleDeMatch(self):
        """
        a partir du site obtnir toutes les liens vers les urls des feuilles de matchs
        out : 
            listePage : liste des urls concernants les matchs d'uen journee
        """
        self.driver.get(self.urlDateJournee)
        time.sleep(10)
        #recuperer la liste des hyperliens qui ont le mot "feuille" dedans
        try :
            #containerScore=WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH,f"//div[@class='snapshot-footer']"))) #si besoin que la ligne dessous ne fonctionne pas
            elementsScore=WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, f"//a[@class='sib3-game-url stats-boxscore game-status-3']")))
        except TimeoutException :
            raise PasDeMatchError(self.dateJournee)
        return [p.get_attribute("href") for p in elementsScore]
    
    def dicoMatchs(self):
        """
        en fonction de la source, creer les dfs des matchs et stats, dans un dico
        """
        dicoJournee={}
        if self.sourceDonnees=='internet' : 
            for e,p in enumerate(self.getListFeuilleDeMatch()) :
                print(e,p)
                #ouvrir la page
                self.driver.get(p)
                #rafraichier le driver
                self.driver.refresh()
                time.sleep(5)
                self.driver.implicitly_wait(20)
                dicoJournee[e]={'match':pd.read_html(self.driver.page_source)[0]}
                time.sleep(5)
                self.driver.implicitly_wait(20)
                dicoJournee[e]['stats_e0']=pd.read_html(self.driver.page_source)[2]
                self.driver.implicitly_wait(20)
                time.sleep(5)
                #naviguer dans les elemnts pour atteindre le boutton de changement d'equipe
                ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
                elementStatButton=WebDriverWait(self.driver, 10,ignored_exceptions=ignored_exceptions).until(EC.element_to_be_clickable((
                    By.XPATH, "//a[@class='pills-button pills-button__right ng-binding']")))
                #changer d'euipe et stocker
                elementStatButton.click()
                self.driver.implicitly_wait(20)
                dicoJournee[e]['stats_e1']=pd.read_html(self.driver.page_source)[2]
            self.miseEnFormeDf(dicoJournee) 
        elif self.sourceDonnees=='csv' :
            dossierCsvEnCours=os.path.join(self.dossierExportCsv,self.dateJournee)
            with os.scandir(dossierCsvEnCours) as it:
                listEntry=[(entry.name[1],os.path.join(dossierCsvEnCours,entry.name),'match' if 'equipe' not in entry.name else f'stats_e{i%3-1}') 
                           for i,entry in enumerate(it) if entry.name.endswith('.csv') and entry.is_file()]
            dicoJournee={}
            for i,e in enumerate(listEntry) :
                a,b,c=e
                if i%3==0 : 
                    dicoJournee[int(a)]={c:pd.read_csv(b,index_col='Unnamed: 0')}
                else : 
                    dicoJournee[int(a)][c]=pd.read_csv(b,index_col='Unnamed: 0')  
            #ICI IL FAUT REMETTRE EN FORME LE CSV
        return dicoJournee
    
    def miseEnFormeDf(self, dicoJournee):
        """
        mettre en forme les attributs des df du dicoJournee (supprimer les attributs non utiles,
        renommer les autres
        in : 
            dicoJournee : dico des matchs et stats non mis en forme
        """
        for i in range(len(dicoJournee)) :
            self.colonnesMatch(dicoJournee[i]['match']) #modifier le noms de colonnes
            for e in ('stats_e0','stats_e1') : 
                self.colonnesStats(dicoJournee[i][e])
                #ajouter ttributs manqants et mettre en forme
                self.ajoutAttributs(dicoJournee[i][e]) #ajouter les attributs supplementaires
    
    def colonnesMatch(self,dfMatch,nomsColonnesMatch=nomsColonnesMatch):
        """
        modifier les noms de colonnees dans une df de match, gestion ds prolongations
        """
        nbColonnesMatch=len(dfMatch.columns) - len(nomsColonnesMatch)
        if nbColonnesMatch > 0 : 
            prolongation=[f'pr{i+1}' for i in range(nbColonnesMatch)]
            nomsColonnesMatch=nomsColonnesMatch[:-1]+prolongation+[nomsColonnesMatch[-1]]
        dfMatch.columns=nomsColonnesMatch
        
    def colonnesStats(self,dfStats):
        """
        modifier les noms des colonnes, supprimer les inutiles, supprimer la ligne de fin
        """
        if dfStats.columns.tolist() != nomsColonnesStat : #sinon nrmalement ça veut dire que la mise en forme a été faite avant
            dfStats.columns=nomsColonnesStat
            dfStats.drop('nom.1', axis=1, inplace=True)
            dfStats.drop(dfStats.loc[dfStats.minute=='240:00'].index, inplace=True)
        
                
    def ajoutAttributs(self,dfStatEquipe):
        """
        ajouter les attributs did not play, blesse, score_ttfl aux df relatives aux equipes
        in : 
           dfStatEquipe : df de stats des equipes issues du dico des matchs et stats mis en forme issu sde miseEnFormeDf()
        """
        dfStatEquipe['dnp']=dfStatEquipe.minute.apply(lambda x : any([e in x for e in dnpTupleTexte])  or x=='00:00')
        dfStatEquipe['blesse']=dfStatEquipe.minute.apply(lambda x : "Injury / Illness" in x)
        #passer les valeurs des joueurs n'ayant pas joues a NaN
        dfStatEquipe.loc[dfStatEquipe.dnp,
            [c for c in dfStatEquipe.columns if c not in ('nom','dnp','blesse')]]=np.NaN
        #convertir en format float les donnees numeriques
        for c in [e for e in dfStatEquipe.columns if e not in ('nom', 'position', 'minute', 'dnp', 'blesse')] :
                dfStatEquipe[c]=dfStatEquipe[c].astype(float)
        #convertir le temps joue en format date
        dfStatEquipe['minute']=dfStatEquipe.minute.apply(lambda x : 
                    pd.to_timedelta('00:'+x) if not pd.isnull(x) else pd.to_timedelta(x,unit='S'))
        #simplifier les noms en enlevant les espaces en trop
        dfStatEquipe['nom']=dfStatEquipe.nom.apply(lambda x : ' '.join(x.split()))
        #score ttfl
        dfStatEquipe.loc[~dfStatEquipe.dnp,'score_ttfl']=dfStatEquipe.loc[~dfStatEquipe.dnp].apply(lambda x : sum([x[c] for c in ('points', 'rebonds', 'passes_dec', 'steal','contres', 'tir_reussi',
                                    'trois_pt_r','lanc_frc_r')]) - (x['ball_perdu']+(x['tir_tentes']-x['tir_reussi'])+
                                                                  (x['trois_pt_r']-x['trois_pt_t']) + 
                                                                  (x['lanc_frc_r']-x['lanc_frc_t'])), axis=1)
        
    
    def creerDossierJournee(self):
        """
        creer un dossier pour y stocker les fichiers csv d'une journee telechargee
        """
        if not os.path.exists(self.dossierDate):
            os.makedirs(self.dossierDate)
        return
    
    def saveCsv(self):
        """
        sauvegarder les df du dico Journee en csv
        """    
        self.creerDossierJournee()
        for k,v in self.dicoJournee.items() : 
            for i,j in v.items():
                if i=='match' : 
                    j.to_csv(os.path.join(self.dossierDate,f'm{k}_{self.dateJournee}.csv'), index=False)
                else : 
                    j.to_csv(os.path.join(self.dossierDate,f'm{k}_equipe{i[-1]}_{self.dateJournee}.csv'),index=False)
  
class JoueursSiteNba(object):  
    """
    classes pour récupérer les joueurs depuis le site de la nba
    le principe : 
    1. connexion au site
    2. balalyer les lettres iinitiales des noms
    3. concatener puis mettre en forme un df
    """
    
    def __init__(self, urlPageJoueurs='https://fr.global.nba.com/playerindex/',
                 nomClassDivContainer='hidden-sm col-sm-9 col-lg-10 letters-wrap'):
        """
        Attributes : 
            driver : driver Selenium pour firefox. cf CreationDriverFirefox()
            urlPageJoueurs : url de la page des joueurs
            nomClassDivContainer : nom de la div qui contient les lettres a faire defiler
            dfJoueurs : dataframe descriptives des joueurs (nom, equipe, taille, poids, position, experience, pays, date_entree_nba
        """
        self.driver=CreationDriverFirefox()
        self.urlPageJoueurs=urlPageJoueurs
        self.driver.get(urlPageJoueurs)
        self.nomClassDivContainer=nomClassDivContainer
        self.dfJoueurs=self.miseEnFormeDfJoueurs(self.creerDfJoueurs())
    
    def getlisteBouttonLettre(self):
        """
        obetnir le container 
        """
        ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
        containerBouttonLettre=WebDriverWait(self.driver, 10,ignored_exceptions=ignored_exceptions).until(EC.element_to_be_clickable((
                    By.XPATH, f"//div[@class='{self.nomClassDivContainer}']")))
        listBouttonLettre=WebDriverWait(containerBouttonLettre, 10,ignored_exceptions=ignored_exceptions).until(EC.presence_of_all_elements_located((
                    By.XPATH, ".//*")))
        return listBouttonLettre
    
    def creerDfJoueurs(self):
        """
        à partir du driver de la classe, creer une df en balyant la page contenant le nom des joueurs
        """
        listBouttonLettre=self.getlisteBouttonLettre()
        dico={}
        for i,e in enumerate(listBouttonLettre) : 
            e.click()
            time.sleep(3)
            dico[i]=pd.read_html(self.driver.page_source)
        dfJoueurs=pd.concat([v[0] for v in dico.values()])
        return dfJoueurs
    
    def miseEnFormeDfJoueurs(self,dfJoueurs ):
        """
        modification des noms d'attributs, et certains type
        """
        dfJoueursForme=dfJoueurs.drop('Unnamed: 1',axis=1).rename(
            columns={'Joueur':'nom','Équipe':'equipe','POS':'position','Taille':'taille',
                     'OUEST':'poids', 'EXP':'experience','Pays':'pays'})
        dfJoueursForme['poids']=dfJoueursForme.poids.apply(lambda x : float(x[:-3]))
        dfJoueursForme['date_entree_nba']=dfJoueursForme['experience'].apply(lambda x : pd.to_datetime('2020-10-01') - 
                                          pd.to_timedelta(x*365.25, unit='D')).dt.date
        dfJoueursForme['nom']=dfJoueursForme.nom.apply(lambda x : ' '.join(x.split()))
        dfJoueurs.reset_index(drop=True, inplace=True)
        return dfJoueursForme
        
  
class PasDeMatchError(Exception):  
    """
    erreur levee si pas de match à une date donnee
    """ 
    def __init__(self,dateJournee):
        self.dateJournee=dateJournee
        super().__init__(f'Pas de match le {dateJournee}')