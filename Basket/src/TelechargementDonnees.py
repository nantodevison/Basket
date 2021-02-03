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
from selenium.webdriver.support.ui import Select
import time, os, re
import pandas as pd
import numpy as np
from collections import Counter

urlSiteNbaScore='https://www.nba.com/games'
nomsColonnesStat=['nom', 'minute','tir_reussi','tir_tentes', 'pct_tir', 'trois_pt_r', 'trois_pt_t', 'pct_3_pt','lanc_frc_r', 'lanc_frc_t', 'pct_lfrc',
 'rebonds_o', 'rebonds_d', 'rebonds', 'passes_dec', 'steal','contres','ball_perdu', 'faute_p','points', 'plus_moins']
nomsColonnesMatch=['equipe','q1','q2','q3','q4','final']
dnpTupleTexte=("Pas en tenue","N'a pas joué", "Pas avec l'équipe","DNP","NWT","DND")
ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)

def gererCookie(driver):
    """
    si sur la page joueur un cookie apparait je veux pouvoir le clicker
    """
    time.sleep(5)
    try : 
        boutonCookie=WebDriverWait(driver, 10,ignored_exceptions=ignored_exceptions).until(EC.element_to_be_clickable((
                By.XPATH, f"//button[@id='onetrust-accept-btn-handler']")))
        boutonCookie.click()
        time.sleep(3)
    except TimeoutException : 
        pass

def simplifierNomJoueur(nom):
    """
    simplifier un nom (prenom+nom) de joueur pour n'avoir aucun espace aucun caracteres special, tout lie
    """
    return re.sub(' |-|\.|\'','',nom).lower()

class DriverFirefox(object):
    """
    ouvrir un driver Selenium
    on peut le faire de façon automatisee via un context manager (par defaut), ou se le garder ouvert
    avec attribut typeConn != 'Auto'
    attribut : 
        typeConn : string : ouverture dans context manager ou non. default='Auto' i.e context manager
    """
    def __init__(self, typeConn='Auto'):
        """
        on ne cree le self.driver 'en dur' que sur demande explicite
        """
        if typeConn!='Auto' :
            self.driver = webdriver.Firefox()
            self.driver.implicitly_wait(20)
            time.sleep(2)
   
    def __enter__(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(20)
        time.sleep(2)
        return self

    def __exit__(self,*args):
        self.driver.quit()   
        return False

class JourneeSiteNba(object):
    '''
    Resultats des matchs publies sur le site pour une date
    '''

    def __init__(self, dateJournee, dossierExportCsv=r'C:\Users\martin.schoreisz\git\Basket\Basket\data'):
        '''
        Attributes
            dateJournee : string au format YYYY-MM-DD
            urlDateJournee : string : url de la date de la journee
            sourceDonnees : string : soure de la donnees : "internet" ou "csv" si la donnees a ete precedemment chargees depuis le site
            driver : selenium driver firefox
            dossierDate : si on enregistre des csv dossier qui conteint les donnees de la journee
            dicoJournee : dico avec en cle un integer  et en value un dico de 3 clé : match, stats_eO et stat_e1 qui contein les dfs de donnees
            dossierExportCsv : dossier pour export de la journee telechargee
        '''
        self.dateJournee=dateJournee
        self.urlDateJournee=fr'{urlSiteNbaScore}?date={self.dateJournee}'
        self.dossierExportCsv=dossierExportCsv
        with DriverFirefox() as d : 
            self.driver=d.driver
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
        time.sleep(3)
        gererCookie(self.driver)
        #recuperer la liste des hyperliens qui ont le mot "feuille" dedans
        try :
            elementsScore=WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.LINK_TEXT, 'BOX SCORE')))
        except TimeoutException as e :
            print(e)
            raise PasDeMatchError(self.dateJournee)
        return [p.get_attribute("href") for p in elementsScore]
    
    def dicoMatchs(self):
        """
        en fonction de la source, creer les dfs des matchs et stats, dans un dico
        """
        dicoJournee={}
        for e,p in enumerate(self.getListFeuilleDeMatch()) : 
            print(e,p)
            self.driver.get(p)
            time.sleep(7)
            self.driver.implicitly_wait(20)
            #sur l'onglet box-score on recupere les stats des equipes
            dfsEquipes=pd.read_html(self.driver.page_source)
            dicoJournee[e]={'stats_e0':dfsEquipes[0]} 
            dicoJournee[e]['stats_e1']=dfsEquipes[1]
            time.sleep(7)
            self.driver.implicitly_wait(20)
            #bascule sur l'onglet summary er recuperer les stats de matchs: 
            elementSummary=WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.LINK_TEXT, 'Summary')))
            self.driver.execute_script("arguments[0].click();", elementSummary)#passer via Javascript pour clicker mm si qqch devant
            time.sleep(7)
            self.driver.implicitly_wait(20)
            dicoJournee[e]['match']=pd.read_html(self.driver.page_source)[0]
        self.miseEnFormeDf(dicoJournee)
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
        dfStats.drop(dfStats.tail(1).index,inplace=True)
        dfStats.columns=nomsColonnesStat
        dfStats.loc[dfStats.head(5).index,'nom']=dfStats.head(5).nom.str[:-1]
        
                
    def ajoutAttributs(self,dfStatEquipe):
        """
        ajouter les attributs did not play, blesse, score_ttfl aux df relatives aux equipes
        in : 
           dfStatEquipe : df de stats des equipes issues du dico des matchs et stats mis en forme issu sde miseEnFormeDf()
        """
        dfStatEquipe['dnp']=dfStatEquipe.minute.apply(lambda x : any([e in x for e in dnpTupleTexte])  or x=='00:00')
        dfStatEquipe['blesse']=dfStatEquipe.minute.apply(lambda x : "Injury/Illness" in x)
        #passer les valeurs des joueurs n'ayant pas joues a NaN
        dfStatEquipe.loc[dfStatEquipe.dnp,
            [c for c in dfStatEquipe.columns if c not in ('nom','dnp','blesse')]]=np.NaN
        #convertir en format float les donnees numeriques
        for c in [e for e in dfStatEquipe.columns if e not in ('nom', 'position', 'minute', 'dnp', 'blesse')] :
                dfStatEquipe[c]=dfStatEquipe[c].astype(float)
        #convertir le temps joue en format date
        dfStatEquipe['minute']=dfStatEquipe.minute.apply(lambda x : 
                    pd.to_timedelta('00:'+x) if not pd.isnull(x) else pd.to_timedelta(x,unit='S'))
        #simplifier les noms car il le lit 2 fois (je crois que c'est du au differents liens de la page)
        dfStatEquipe['nom']=dfStatEquipe.nom.apply(lambda x : x.split()[0]+' '+x.split()[1][:-2] if Counter(x)[' ']<=2 and x.split()[-1].lower() not in ('jr.', 'sr.', 'ii','iii','iv','v')  
                                             else ' '.join(x.split()[:2]+[x.split()[2][:-2],]))
        #ajouter l'attribut de nom simplifie
        dfStatEquipe['nom_simple']=dfStatEquipe.nom.apply(lambda x : simplifierNomJoueur(x))
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
    2. acceder à liste deroulante et choisir All ('USA')
    3. concatener (France) puis mettre en forme un df
    """
    
    def __init__(self, urlPageJoueurs='https://www.nba.com/players',refWebElement='Page Number Selection Drown Down List',
                 typeExport='All'):
        """
        Attributes : 
            driver : driver Selenium pour firefox. cf CreationDriverFirefox()
            urlPageJoueurs : url de la page des joueurs
            refWebElement : nom de l'element qui permet d'afficher tous les joueurs
            dfJoueurs : dataframe descriptives des joueurs (nom, equipe, taille, poids, position, experience, pays, date_entree_nba
            typeExport = string : pour pouvoir utiliser la classe pour balayer tous les joueurs à la suite ou un seul
        """
        with DriverFirefox() as d :
            self.driver=d.driver
            self.urlPageJoueurs=urlPageJoueurs
            self.refWebElement=refWebElement
            self.driver.get(self.urlPageJoueurs)
            gererCookie(self.driver)
            if typeExport=='All' : 
                self.dfJoueurs=self.miseEnForme(self.obtenirlistLinkJoueurs())
            else : 
                self.dfJoueurs=pd.DataFrame(self.attributJoueur(self.urlPageJoueurs), index=[0])

    def obtenirlistLinkJoueurs(self):
        """
        obetnir le container 
        """
        select = Select(WebDriverWait(self.driver, 10,ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((
                    By.XPATH, f"//select[@title='{self.refWebElement}']"))))
        time.sleep(3)
        select.select_by_value('-1')
        time.sleep(3)
        #recupérer la liste des liens vers les pages des joueurs
        listLinkGeneral=self.driver.find_element_by_xpath("//td[@class='primary text PlayerList_primaryCol__1tWZA']")
        listLinkJoueurs=[a.get_attribute("href") for a in listLinkGeneral.find_elements_by_xpath("//a[@class='flex items-center t6']")]
        return listLinkJoueurs
    
    def attributJoueur(self,linkJoueur, refDivCarac='PlayerSummary_playerInfo__1L8sx',
                       refParagrapheCarac='PlayerSummary_playerInfoValue__mSfou', refElementNom='flex flex-col mb-2 text-white'):
        """
        à partir d'un lien qui pointe vers une page liee à un joueur, retourner un dico des caracteristique
        in : 
            refDivCarac : nom de la div qui contient toute ls caracteristiques
            refParagrapheCarac : nom des balises p qui contiennentt les carac
            refElementNom : nom de la div dqui contient le nom et prenom
        """
        dicoCaracJoueur={}
        self.driver.get(linkJoueur)
        time.sleep(3)
        #trouver toute les caracteristiques (car les nom sde classe sont les mêmes pour tous)
        elements=WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, f"//div[@class='{refDivCarac}']/p[@class='{refParagrapheCarac}']")))
        #self.driver.find_elements_by_xpath(f"//div[@class='{refDivCarac}']/p[@class='{refParagrapheCarac}']")
        try : 
            nomPosition=WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, f"//div[@class='{refElementNom}']")))
            #self.driver.find_element_by_xpath(f"//div[@class='{refElementNom}']")
            listeCaracNomPosition=[e.text for e in nomPosition.find_elements_by_xpath(".//*")]
            dicoCaracJoueur['taille']=[float(re.sub('(\(|\)|m)','',re.search('(\([1-2]\.[0-9]{2}m\))',e.text).group(1))) for i,e in enumerate(elements) if i==0][0]
            dicoCaracJoueur['poids']=[float(re.sub('(\(|\)|kg)','',re.search('(\([0-9]{1,3}kg\))',e.text).group(1))) for i,e in enumerate(elements) if i==1][0]
            dicoCaracJoueur['date_entree_nba']=pd.to_datetime(f"{[2020-int(e.text.split()[0]) if e.text != 'Rookie' else 2020 for i,e in enumerate(elements) if i==7][0]  }-10-01")
            dicoCaracJoueur['date_naissance']=pd.to_datetime([e.text for e in elements if re.match('[a-z]{0,12} [0-9]{1,2}, [0-9]{4}',e.text.lower())][0])
            dicoCaracJoueur['nom']=' '.join(listeCaracNomPosition[-2:])
            dicoCaracJoueur['nom_simple']=simplifierNomJoueur(' '.join(listeCaracNomPosition[-2:]))
            dicoCaracJoueur['id_position_terrain']='-'.join([e[0] if e in ('Center','Guard', 'Forward') else 'NC' for e in listeCaracNomPosition[0].split(' | ')[-1].split('-')])
        except Exception as x :
            print (x, linkJoueur)
        
        return dicoCaracJoueur

    def miseEnForme(self,listLinkJoueurs):
        """
        parcourir la liste des liens vers les joueurs, appeker la fonction de recup des infos et concatener
        """
        dfCaracJoueurs= pd.concat([pd.DataFrame(self.attributJoueur(l), index=[i]) for i,l in enumerate(listLinkJoueurs)], axis=0)
        return dfCaracJoueurs
    
 
class PasDeMatchError(Exception):  
    """
    erreur levee si pas de match à une date donnee
    """ 
    def __init__(self, dateJournee):
        self.dateJournee=dateJournee
        
    def __str__(self): 
        return "Pas de match le : %s" % self.dateJournee