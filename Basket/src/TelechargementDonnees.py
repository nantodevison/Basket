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
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException, TimeoutException
from selenium.webdriver.support.ui import Select
import time, re
from datetime import datetime
import pandas as pd
import numpy as np
from collections import Counter
import Connexion_Transfert as ct
from PyQt5.QtCore import QObject, pyqtSignal
from ParamsWeb import (idBoutonGererCookieNba, classLienMatch_calendrier, boutonGererCookieTtfl, urlSiteNbaScore,
                       divDrapeauIncrustation, boutonCloseIncrustation, boutonCloseConnexionNba, divTestCalendrier,
                       urlPageJoueurs, listeDeroulanteNbPage, classeTableauColonne1, classeLienNom, refDivCarac, refParagrapheCarac,
                       refElementNom, sliderHistorique)
from Outils import checkParamValues


nomsColonnesStat=['nom', 'minute','tir_reussi','tir_tentes', 'pct_tir', 'trois_pt_r', 'trois_pt_t', 'pct_3_pt','lanc_frc_r', 'lanc_frc_t', 'pct_lfrc',
 'rebonds_o', 'rebonds_d', 'rebonds', 'passes_dec', 'steal','contres','ball_perdu', 'faute_p','points', 'plus_moins']
nomsColonnesMatch=['id_equipe','q1','q2','q3','q4','final']
nomsColonnesStatsEquipe=['id_equipe','pts_in_paint','fastbreak_pts','biggest_lead',
                   'pts_banc','tm_rebonds','ball_perdu','tm_ball_perdu','pt_subi_ctrattaq']
dnpTupleTexte=("Pas en tenue","N'a pas joué", "Pas avec l'équipe","DNP","NWT","DND")
ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)


def gererCookieNba(driver):
    """
    si sur la page joueur un cookie apparait je veux pouvoir le clicker
    """
    time.sleep(5)
    try: 
        boutonCookie=WebDriverWait(driver, 10,ignored_exceptions=ignored_exceptions).until(EC.element_to_be_clickable((
                By.XPATH, idBoutonGererCookieNba)))
        boutonCookie.click()
        time.sleep(3)
    except TimeoutException: 
        pass


def gererCookieTtfl(driver):
    """
    si sur la page ttfl un cookie apparait je veux pouvoir le clicker (i.e accepter)
    """
    time.sleep(5)
    try: 
        boutonCookie=WebDriverWait(driver, 10,ignored_exceptions=ignored_exceptions).until(EC.element_to_be_clickable((
                By.XPATH, boutonGererCookieTtfl)))
        boutonCookie.click()
        time.sleep(3)
    except TimeoutException: 
        return 


def fermerIncrustationNba(driver):
    """
    si la page des matchs s'ouvre avec un incrustation devant (pour les dates des matchs a venir par exemple), on la ferme
    """
    time.sleep(5)
    try: 
        boutonFermerIncrustation = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, boutonCloseIncrustation)))
        boutonFermerIncrustation.click()
    except TimeoutException: 
        pass 
    
    
def fermerFenetreConnexion(driver):
    """
    si une fenetre de connexion s'ouvre, la fermer 
    """
    time.sleep(5)
    try:
        boutonFermetureFenetreConnexion = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH,boutonCloseConnexionNba)))
        boutonFermetureFenetreConnexion.click()
    except TimeoutException: 
        pass 
    
    
def fermerFenetreFaçade(driver, elementTest):
    """
    fermer n'impore quelle fenetre qui se place devant
    """
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, elementTest)))
        fermerIncrustationNba(driver)
    except TimeoutException:
        try: 
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, divDrapeauIncrustation)))
            fermerIncrustationNba(driver)
        except TimeoutException:
            fermerFenetreConnexion(driver)
    return


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
    attribut: 
        typeConn: string: ouverture dans context manager ou non. default='Auto' i.e context manager
    """
    def __init__(self, typeConn='Auto'):
        """
        on ne cree le self.driver 'en dur' que sur demande explicite
        """
        if typeConn!='Auto':
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


class Calendrier(QObject):
    """
    récuperer le calendrier depuis le site NBA
    """
    signalJourneeFaite = pyqtSignal(int)
    def __init__(self, id_saison, date_depart, duree):
        """
        attributs: 
            id_saison: integer, identiiant saioson
            date_depart: string format YYYY-MM-DD
            duree: integer:nb de jours apres date de depart
        """
        QObject.__init__(self)
        self.id_saison = id_saison
        self.date_depart = date_depart
        self.duree=duree
        
        
    def telechargerUneJournee(self, dateMatch, driver):
        """
        pour une date donnees, telecharger les matchs de cette date ou lever une erreur si pas de match
        in: 
            dateMatch: string: date au format '%Y-%m-%d'
            driver: dirver firfox de selenium
        out: 
            listMatch: liste de strin composant les lihes internet des pages de match
        """
        try:
            elementsMatch = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(
                (By.XPATH, classLienMatch_calendrier)))
        except TimeoutException as e:
            print(e)
            raise PasDeMatchError(dateMatch)
        listMatch = [p.get_attribute("href") for p in elementsMatch]
        return listMatch


    def telechargerCalendrier(self):
        """
        telecharger les donnees des matchs futurs, avec identifiant de saison, selon une date de depart et une duree
        in:
            
        out:
            dfMatchs: la df des matchs avec equipe dom, equipe_est, date_match et id_saison
        """
        listDfMatchs = []
        print('debut')
        with DriverFirefox() as d:
            print('avant driver')
            driver = d.driver
            print('apres driver')
            for i, dateString in enumerate([d.strftime('%Y-%m-%d') for d in pd.date_range(start=self.date_depart, periods=self.duree)]):
                print(dateString)
                urlDateJournee = fr'{urlSiteNbaScore}?date={dateString}'
                driver.get(urlDateJournee)
                time.sleep(3)
                gererCookieNba(driver)
                fermerFenetreFaçade(driver, divTestCalendrier)
                try:
                    listMatch = self.telechargerUneJournee(dateString, driver)
                except PasDeMatchError as e: 
                    print(e)
                    continue
                listDfMatchs.append(pd.DataFrame.from_records([(m.split('-vs-')[0][-3:].upper(), m.split('-vs-')[1][:3].upper(), dateString, self.id_saison
                                                                ) for m in listMatch if '-vs-' in m], 
                      columns=['equipe_exterieure', 'equipe_domicile', 'date_match', 'id_saison']).drop_duplicates())
                self.signalJourneeFaite.emit(i+1)
        self.calendrier = pd.concat(listDfMatchs)
    
    
    def exporterVersBdd(self,bdd='basket'):    
        with ct.ConnexionBdd(bdd) as c:
            self.calendrier.to_sql('calendrier', c.sqlAlchemyConn, schema='donnees_source', if_exists='append', index=False)
   
   
class Blessures(object):
    """
    class permettant d'avoir acces aux joueurs blesses depuis le site de CBS
    """   
    
    
    def __init__(self,dateMaxi, siteCbs='https://www.cbssports.com/nba/injuries'):
        """
        attributs:
            siteCbs: string: adresse du site reference
            dateMaxi: string format YYYY-MM-DD date maximale de recherche des blessures: au dela on ne cherche pas
        """
        self.dateMaxi=dateMaxi
        self.siteCbs=siteCbs
        self.recupererTypeBlessure()
        with DriverFirefox() as d:
            self.driver=d.driver
            self.dfInjuries=self.miseEnFormeBlessures(self.creerDfJoueursBlesses())
          
            
    def recupererTypeBlessure(self,bdd='basket'):
        """
        recuperer le type de blessure et le nom anglais depuis la Bdd
        """
        with ct.ConnexionBdd(bdd) as c: 
            self.dftypeBlessure=pd.read_sql("""SELECT id_type_blessure, nom_blessure, LOWER(nom_blessure_anglais) "Injury"
                                FROM donnees_source.enum_type_blessure""", c.sqlAlchemyConn)
          
            
    def creerDfJoueursBlesses(self):
        """
        recuperer la df de tous les joueurs blesses
        """
        self.driver.get(self.siteCbs)
        time.sleep(5)
        importPage=pd.read_html(self.driver.page_source)
        dfsInjuries=pd.concat([importPage[i] for i in range(len(importPage))])
        return dfsInjuries
    
    
    def miseEnFormeBlessures(self,dfsInjuries):
        """
        mettre en forme les donnees du site, en particulier la mise en forme du nom,
        l'ajout de l'attribut nom_simple, le passage en minuscule des blessures et 
        l'ajout de l'attribut id_type_blessure issu de la Bdd
        """
        dfsInjuries['Player']=dfsInjuries.Player.apply(lambda x: ' '.join(x.split()[-2:]) if Counter(x)[' ']<=4 
                         and x.split()[-1].lower() not in ('jr.', 'sr.', 'ii','iii','iv','v')  
                         else ' '.join(x.split()[-3:])).tolist()
        dfsInjuries['nom_simple']=dfsInjuries.Player.apply(lambda x: simplifierNomJoueur(x))
        dfsInjuries['Injury']=dfsInjuries.Injury.str.lower()
        dfsInjuriesComplet=dfsInjuries.merge(self.dftypeBlessure, on='Injury')
        dfsInjuriesComplet['date_blessure']=dfsInjuriesComplet.Updated.apply(lambda x: pd.to_datetime(x.split(', ')[1]+' '+str(datetime.now().year)) if 
                                                                       pd.to_datetime(x.split(', ')[1]+' '+str(datetime.now().year))<datetime.now() else
                                                                       pd.to_datetime(x.split(', ')[1]+' '+str(datetime.now().year-1))  )
        dfsInjuriesComplet=dfsInjuriesComplet.loc[dfsInjuriesComplet.date_blessure<=self.dateMaxi].copy()
        return dfsInjuriesComplet


class JourneeSiteNba(Blessures, QObject):
    '''
    Resultats des matchs publies sur le site pour une date
    '''
    signalAvancement=pyqtSignal(str)
    signalMatchFait=pyqtSignal(int)
    
    
    def __init__(self, dateJournee):
        '''
        Attributes
            dateJournee: string au format YYYY-MM-DD
            urlDateJournee: string: url de la date de la journee
            sourceDonnees: string: soure de la donnees: "internet" ou "csv" si la donnees a ete precedemment chargees depuis le site
            driver: selenium driver firefox
            dossierDate: si on enregistre des csv dossier qui conteint les donnees de la journee
            dicoJournee: dico avec en cle un integer  et en value un dico de 3 clé: match, stats_eO et stat_e1 qui contein les dfs de donnees
            dossierExportCsv: dossier pour export de la journee telechargee
        '''
        QObject.__init__(self)
        self.dateJournee=dateJournee
        Blessures.__init__(self, self.dateJournee)
        self.urlDateJournee=fr'{urlSiteNbaScore}?date={self.dateJournee}'
        with DriverFirefox() as d: 
            self.driver=d.driver
            self.listFeuilleDeMatch, self.nbMatchs=self.getListFeuilleDeMatch()
        
        
    def __str__(self):
        return '\n'.join([f'match {i} \n'+ v['match'].to_string(columns=['equipe', 'final'], index=False,
                    header=False) for i,v in enumerate(self.dicoJournee.values())])
    
    
    def getListFeuilleDeMatch(self):
        """
        a partir du site obtnir toutes les liens vers les urls des feuilles de matchs
        out: 
            listePage: liste des urls concernants les matchs d'uen journee
        """
        self.driver.get(self.urlDateJournee)
        time.sleep(3)
        gererCookieNba(self.driver)
        #recuperer la liste des hyperliens qui ont le mot "feuille" dedans
        try:
            elementsScore=WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.LINK_TEXT, 'BOX SCORE')))
        except TimeoutException:
            raise PasDeMatchError(self.dateJournee)
        return [p.get_attribute("href") for p in elementsScore], len(elementsScore)
    
    
    def dicoMatchs(self):
        """
        en fonction de la source, creer les dfs des matchs et stats, dans un dico
        """
        dicoJournee={}
        with DriverFirefox() as d: 
            self.driver=d.driver
            for e,p in enumerate(self.listFeuilleDeMatch): 
                print(e,p)
                self.signalAvancement.emit(f'{p[25:35]}...')
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
                dicoJournee[e]['stats_equipes']=pd.concat([dicoJournee[e]['match'][['Unnamed: 0']],
                                                          pd.read_html(self.driver.page_source)[1]],axis=1)
                self.signalMatchFait.emit(e+2)
        self.miseEnFormeDf(dicoJournee)
        self.dicoJournee=dicoJournee
    
    
    def miseEnFormeDf(self, dicoJournee):
        """
        mettre en forme les attributs des df du dicoJournee (supprimer les attributs non utiles,
        renommer les autres
        in: 
            dicoJournee: dico des matchs et stats non mis en forme
        """
        for i in range(len(dicoJournee)):
            self.colonnesMatch(dicoJournee[i]['match'],dicoJournee[i]['stats_equipes'] ) #modifier le noms de colonnes
            for e in ('stats_e0','stats_e1'): 
                self.colonnesStats(dicoJournee[i][e])
                #ajouter ttributs manqants et mettre en forme
                self.ajoutAttributs(dicoJournee[i][e]) #ajouter les attributs supplementaires
    
    
    def colonnesMatch(self,dfMatch,dfStatsEquipes,nomsColonnesMatch=nomsColonnesMatch,
                      nomsColonnesStatsEquipe=nomsColonnesStatsEquipe):
        """
        modifier les noms de colonnees dans une df de match, gestion ds prolongations
        """
        nbColonnesMatch=len(dfMatch.columns) - len(nomsColonnesMatch)
        if nbColonnesMatch > 0: 
            prolongation=[f'pr{i+1}' for i in range(nbColonnesMatch)]
            nomsColonnesMatch=nomsColonnesMatch[:-1]+prolongation+[nomsColonnesMatch[-1]]
        dfMatch.columns=nomsColonnesMatch
        dfStatsEquipes.columns=nomsColonnesStatsEquipe
        
        
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
        in: 
           dfStatEquipe: df de stats des equipes issues du dico des matchs et stats mis en forme issu sde miseEnFormeDf()
        """
        def trouverDnp(minute):
            """
            trouver les dnp, en fonction du nombre de minute ou des annotations
            """
            if isinstance(minute, float) or isinstance(minute, int): 
                if minute==0: 
                    return True 
                else: 
                    return False 
            elif isinstance(minute, str): 
                if any([e in minute for e in dnpTupleTexte])  or float(minute.replace(':','.'))==0:
                    return True 
                else: 
                    return False 
            else: 
                raise TypeError('donnees minutes non traitees dans recherche dnp')
              
                
        def convertirMinute(minute):
            """
            convertir les minutes en timedelta
            """
            if pd.isnull(minute): 
                return pd.to_timedelta(minute,unit='S')
            elif isinstance(minute, str): 
                return pd.to_timedelta('00:'+':'.join([a.zfill(2) for a in str(minute).split('.')]))
            elif isinstance(minute, float): 
                return pd.to_timedelta('00:'+':'.join([a.zfill(2) for a in str(minute).split('.')]))
            elif isinstance(minute, int):
                return f'{str(minute).zfill(2)}:00'
            else:
                raise TypeError('type de donnees minutes non gere')
            
            
        dfStatEquipe['dnp']=dfStatEquipe.minute.apply(lambda x: trouverDnp(x))
        dfStatEquipe['blesse']=dfStatEquipe.minute.apply(lambda x: "Injury/Illness" in x if isinstance(x, str) else False)
        #passer les valeurs des joueurs n'ayant pas joues a NaN
        dfStatEquipe.loc[dfStatEquipe.dnp,
            [c for c in dfStatEquipe.columns if c not in ('nom','dnp','blesse')]]=np.NaN
        #convertir en format float les donnees numeriques
        for c in [e for e in dfStatEquipe.columns if e not in ('nom', 'position', 'minute', 'dnp', 'blesse')]:
                dfStatEquipe[c]=dfStatEquipe[c].astype(float)
        #convertir le temps joue en format date
        dfStatEquipe['minute']=dfStatEquipe.minute.apply(lambda x: convertirMinute(x))
        #simplifier les noms car il le lit 2 fois (je crois que c'est du au differents liens de la page)
        dfStatEquipe['nom']=dfStatEquipe.nom.apply(lambda x: x.split()[0]+' '+x.split()[1][:-2] if Counter(x)[' ']<=2 and x.split()[-1].lower() not in ('jr.', 'sr.', 'ii','iii','iv','v')  
                                             else ' '.join(x.split()[:2]+[x.split()[2][:-2],]))
        #ajouter l'attribut de nom simplifie
        dfStatEquipe['nom_simple']=dfStatEquipe.nom.apply(lambda x: simplifierNomJoueur(x))
        #score ttfl
        dfStatEquipe.loc[~dfStatEquipe.dnp,'score_ttfl']=dfStatEquipe.loc[~dfStatEquipe.dnp].apply(lambda x: sum([x[c] for c in ('points', 'rebonds', 'passes_dec', 'steal','contres', 'tir_reussi',
                                    'trois_pt_r','lanc_frc_r')]) - (x['ball_perdu']+(x['tir_tentes']-x['tir_reussi'])+
                                                                  (x['trois_pt_t']-x['trois_pt_r']) + 
                                                                  (x['lanc_frc_t']-x['lanc_frc_r'])), axis=1)
  
  
class JoueursSiteNba(object):  
    """
    classes pour récupérer les joueurs depuis le site de la nba
    le principe: 
    1. connexion au site
    2. acceder à liste deroulante et choisir All ('USA')
    3. concatener (France) puis mettre en forme un df
    """
    
    
    def __init__(self, anneeRef, typeExport='All', historiqueComplet=False, liensMano=None):
        """
        Attributes: 
            anneeRef: integer: annee de reference, i.e annee de la derniere draft ayant eu lieu
            historiqueComplet: booleen: si c'est vrai, ça clique le bouton pour obtenir toute la liste des joueurs de tout les temps, sinon, juste les joueuers actuels
            driver: driver Selenium pour firefox. cf CreationDriverFirefox()
            dfJoueurs: dataframe descriptives des joueurs (nom, equipe, taille, poids, position, experience, pays, date_entree_nba
            typeExport = string: pour pouvoir utiliser la classe pour balayer tous les joueurs à la suite, seulement ceux inconnus en bdd ou une liste fournie.
                                  valeur possible: 'All', 'Mano'
            liensMano: string: adresse internetde la page du joueur a recuperer
        """
        checkParamValues(typeExport, ['All', 'Mano'])
        with DriverFirefox() as d:
            self.anneeRef = anneeRef
            self.driver = d.driver
            self.typeExport = typeExport
            self.historiqueComplet = historiqueComplet
            self.driver.get(urlPageJoueurs)
            gererCookieNba(self.driver)
            if self.typeExport == 'All':
                self.listLinkJoueurs = self.obtenirlistLinkJoueurs()
            elif self.typeExport == 'Mano':
                if not liensMano or (not isinstance(liensMano, list) and not isinstance(liensMano, tuple)): 
                    raise ValueError('liensMano ne doit pas etre de type NoneType ou doit etre une liste ou un tuple')
                else:
                    self.listLinkJoueurs = liensMano 
            self.creerDfJoueur()


    def obtenirlistLinkJoueurs(self):
        """
        obetnir le container 
        """
        if self.historiqueComplet:
            print('slider a cocher')
            slider = WebDriverWait(self.driver,15).until(EC.visibility_of_element_located((By.XPATH, f"//span[@class='{sliderHistorique}']")))
            self.driver.execute_script("arguments[0].click();", slider)
        select = Select(WebDriverWait(self.driver, 10, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((
                    By.XPATH, f"//select[@title='{listeDeroulanteNbPage}']"))))
        time.sleep(3)
        select.select_by_value('-1')
        time.sleep(3)
        #recupérer la liste des liens vers les pages des joueurs
        listLinkGeneral = self.driver.find_element_by_xpath(f"//td[@class='{classeTableauColonne1}']")
        listLinkJoueurs = [a.get_attribute("href") for a in listLinkGeneral.find_elements(by=By.XPATH, value=f"//a[@class='{classeLienNom}']")]
        return listLinkJoueurs
    
    
    def attributJoueur(self, linkJoueur):
        """
        à partir d'un lien qui pointe vers une page liee à un joueur, retourner un dico des caracteristique
        in: 
            refDivCarac: nom de la div qui contient toute ls caracteristiques
            refParagrapheCarac: nom des balises p qui contiennentt les carac
            refElementNom: nom de la div dqui contient le nom et prenom
        """
        dicoCaracJoueur = {}
        self.driver.get(linkJoueur)
        time.sleep(3)
        #trouver toute les caracteristiques (car les nom sde classe sont les mêmes pour tous)
        try:
            elements = WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((
                By.XPATH, f"//div[@class='{refDivCarac}']/p[@class='{refParagrapheCarac}']")))
        except TimeoutException:
            print(f'element non trouve a adresse {linkJoueur}')
            return []
        #try: 
        nomPosition = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, f"//div[@class='{refElementNom}']")))
        #self.driver.find_element_by_xpath(f"//div[@class='{refElementNom}']")
        listeCaracNomPosition = [e.text for e in nomPosition.find_elements(by=By.XPATH, value=".//*")]
        """
        dicoCaracJoueur['taille'] = [float(re.sub('(\(|\)|m)','',re.search('(\([1-2]\.[0-9]{2}m\))',e.text).group(1))) for i,e in enumerate(elements) if i==0][0]
        dicoCaracJoueur['poids'] = [float(re.sub('(\(|\)|kg)','',re.search('(\([0-9]{1,3}kg\))',e.text).group(1))) for i,e in enumerate(elements) if i==1][0]
        dicoCaracJoueur['draft'] = elements[5].text
        dicoCaracJoueur['date_naissance'] = pd.to_datetime([e.text for e in elements if re.match('[a-z]{0,12} [0-9]{1,2}, [0-9]{4}',e.text.lower())][0])"""
        # caracteristiques physiques
        textTaille = elements[0].text
        textPoids = elements[1].text
        textPays = elements[2].text
        if len(elements) == 11:
            textDateNaissance = elements[4].text
            textDraft = elements[5].text
            textExperience = elements[6].text
        elif len(elements) == 12:
            textDateNaissance = elements[5].text
            textDraft = elements[6].text
            textExperience = elements[7].text
        try:
            dicoCaracJoueur['taille'] = float(re.sub('(\(|\)|m)','',re.search('(\([1-2]\.[0-9]{2}m\))',textTaille).group(1)))
        except AttributeError: 
            dicoCaracJoueur['taille'] = np.nan
        try:
            dicoCaracJoueur['poids'] = float(re.sub('(\(|\)|kg)','',re.search('(\([0-9]{1,3}kg\))',textPoids).group(1))) if textPoids else np.nan
        except AttributeError: 
            dicoCaracJoueur['poids'] = np.nan
        dicoCaracJoueur['pays'] = textPays
        dicoCaracJoueur['date_naissance'] = pd.to_datetime(textDateNaissance)
        dicoCaracJoueur['draft'] = textDraft
        #caracteristiques de joueur
        dicoCaracJoueur['experience'] = textExperience
        dicoCaracJoueur['nom'] = ' '.join(listeCaracNomPosition[1:3])
        dicoCaracJoueur['nom_simple'] = simplifierNomJoueur(' '.join(listeCaracNomPosition[1:3]))
        dicoCaracJoueur['id_position_terrain'] = '-'.join([e[0] if e in ('Center','Guard', 'Forward') else 'NC' for e in 
                                                           listeCaracNomPosition[0].split(' | ')[-1].split('-')])   
        dicoCaracJoueur['page_web'] =  linkJoueur
        #except Exception as x:
            #print (x, linkJoueur)
        return dicoCaracJoueur

    
    def creerDfJoueur(self):
        """
        creer la df des joueurs selon le type d'export souhaite
        """
        if self.typeExport in ('All', 'Mano'): 
                self.dfJoueurs = pd.concat([pd.DataFrame(self.attributJoueur(l), index=[i]) for i,l in enumerate(self.listLinkJoueurs)], axis=0)
        else: 
            self.dfJoueurs = pd.DataFrame(self.attributJoueur(urlPageJoueurs), index=[0])


class JoueursChoisisTtfl(object):
    """
    class des joueurs choisis en ttfl par le passé
    pour le moment il y a 2 sources de données: 
    - l'enregistrement de pages html depuis le site de trashtalk, 
    - les données stockées en base
    """
    
    
    def __init__(self, saison, htmlTtfl='https://fantasy.trashtalk.co/?tpl=historique'):
        """
        attributs: 
        htmlTtfl: strinf url de la TTFL
        fichiersHtml: tuple ou list des fichiers html telecharges au prealable depuis l'historique de trashtalk https://fantasy.trashtalk.co/?tpl=historique
        dfJoueursChoisisBdd:df des joueurs deja choisi stockes dans la bdd
        """
        self.htmlTtfl=htmlTtfl
        self.saison=saison
        with DriverFirefox() as d:
            self.driver=d.driver
            self.driver.get(self.htmlTtfl)
            time.sleep(3)
            self.recupSiteTrashtalk()
            time.sleep(3)
            self.dfJoueurAInserer=self.filtrerJoueurDejaBdd()
        
        
    def recupSiteTrashtalk(self, titrePageConnexion='#TTFL - Saison 7', titrePageTTFl='Dashboard | TRASHTALK FANTASY'):    
        """
        vérifier si la connexion de __init__ nous dirige directement sur la page TTFL ou sur la page d'accueil
        in: 
           titrePageConnexion: string: titre de la page de connexion (i.e entrer login et mdp)
           titrePageTTFl:  string: titre de la page d'accueil de TTFL (i.e deja connecte)
        """
        if self.driver.title==titrePageConnexion:
            print('connexion a etablir') 
            gererCookieTtfl(self.driver)
            self.ouvrirPageConnexion()
            self.connexion()
            dfJoueursChoisisBase=self.agregationJoueursChoisis(self.accesHistorique())
            self.formeDfJoueursChoisisTrashtalk(dfJoueursChoisisBase)
            #return 'pageConnexion'
        elif self.driver.title==titrePageTTFl: 
            print('connexion deja etablie')
            dfJoueursChoisisBase=self.agregationJoueursChoisis(self.accesHistorique())
        else: 
            raise NameError('le titre de la page ne correspond pas aux titres connus')
        
        
    def ouvrirPageConnexion(self):
        """
        depuis la page d'accueil TTFL non connecte, ouvrir la page de connexion
        """
        time.sleep(3)
        boutonConnexion=WebDriverWait(self.driver, 10,ignored_exceptions=ignored_exceptions).until(EC.element_to_be_clickable((
                By.XPATH, f"//li/a[@href='#login']")))
        boutonConnexion.click()
    
    
    def recupLoginMdp(self, cheminFichier=r'C:\Users\martin.schoreisz\git\Basket\Basket\src\ConnexionId'):
        """
        récupérer les login et mdp depuis le fichier de stockage (en .gitignore)
        in: 
            cheminFichier: path du fichier de stockage
        """
        with open(cheminFichier,'r') as f_id:
            for texte in f_id:
                login, mdp=texte.strip().split(' ')[0],texte.strip().split(' ')[1]
        return login, mdp
    
    
    def connexion(self):
        """
        se connecter a mon compte de TTFL
        """
        time.sleep(3)
        textLogin=WebDriverWait(self.driver, 10,ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((
                By.XPATH, f"//input[@name='email']")))
        textMdp=WebDriverWait(self.driver, 10,ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((
                        By.XPATH, f"//input[@name='password']")))
        boutonLogin=WebDriverWait(self.driver, 10,ignored_exceptions=ignored_exceptions).until(EC.element_to_be_clickable((
                        By.XPATH, f"//button[@class='btn btn-primary font-montserrat all-caps fs-12 pull-right xs-pull-left']")))
        login, mdp=self.recupLoginMdp()
        textLogin.send_keys(login)
        textMdp.send_keys(mdp)
        time.sleep(3)
        boutonLogin.click()
        time.sleep(2)
        
        
    def accesHistorique(self):
        """
        acceder à la page de l'historique et recuperer le nb de page
        """
        boutonHistorique=WebDriverWait(self.driver, 10,ignored_exceptions=ignored_exceptions).until(EC.element_to_be_clickable((
                By.XPATH, f"//li/a[@href='/?tpl=historique']")))
        boutonHistorique.click()
        time.sleep(2)
        pagination=WebDriverWait(self.driver, 10,ignored_exceptions=ignored_exceptions).until(EC.presence_of_all_elements_located((
                By.XPATH, f"//ul[@class='pagination']//a")))
        longueurPagination=len(pagination)-2
        return longueurPagination
    
    
    def agregationJoueursChoisis(self,longueurPagination): 
        """
        parcourir les pages et recuperer les joueurs deja joues
        """
        listDfJoueursChoisis=[]
        for i in range(longueurPagination): 
            time.sleep(2)
            pagination=WebDriverWait(self.driver, 10,ignored_exceptions=ignored_exceptions).until(EC.presence_of_all_elements_located((
                        By.XPATH, f"//ul[@class='pagination']//a")))
            pagination[i+1].click()
            time.sleep(2)
            listDfJoueursChoisis.append(pd.read_html(self.driver.page_source)[0])  
        return pd.concat(listDfJoueursChoisis).iloc[:-1]
    
    
    def formeDfJoueursChoisisTrashtalk(self,dfJoueurChoisis):
        """
        mettre en forme la df des joueurs issus de trashtalk
        in: 
            dfJoueurChoisis: df des joueurs telles que importee du site
        out: 
            dfJoueurChoisiId : df des joueurs telles que importee du site, avec Date, Joueur, nom_simple, id_joueur
        """
        dfJoueurChoisis['nom_simple']=dfJoueurChoisis.Joueur.apply(lambda x:  simplifierNomJoueur(x))
        with ct.ConnexionBdd('basket','maison') as c: 
            dfJoueur=pd.read_sql("select id_joueur, nom_simple from donnees_source.joueur", c.sqlAlchemyConn)
            self.dfJoueurChoisiId=dfJoueurChoisis.merge(dfJoueur, on='nom_simple')
            self.dfJoueurChoisiId['Date']=pd.to_datetime(self.dfJoueurChoisiId.Date)
    
    
    def recupJoueurChoisiBdd(self):
        """
        recuperer les joueurs deja dans la base comme ayant été choisi
        """
        with ct.ConnexionBdd('basket','maison') as c: 
            dfJoueurChoisisBdd=pd.read_sql("SELECT * FROM ttfl.joueurs_choisis;", c.sqlAlchemyConn)
            dfJoueurChoisisBdd['date_choix']=pd.to_datetime(dfJoueurChoisisBdd.date_choix)
        return dfJoueurChoisisBdd
    
    
    def filtrerJoueurDejaBdd(self):
        """
        filtrer les joueurs issus des fichiers html deja dans la bdd
        """
        dfJoueurChoisisBdd=self.recupJoueurChoisiBdd()
        return self.dfJoueurChoisiId.loc[~(self.dfJoueurChoisiId.Date.isin(dfJoueurChoisisBdd.date_choix) & self.dfJoueurChoisiId.id_joueur.isin(dfJoueurChoisisBdd.id_joueur))]
 
 
    def transfertBdd(self):
        """
        transferer les joueurs choisis  non presents dans la bdd
        """
        with ct.ConnexionBdd('basket','maison') as c:
            self.dfJoueurAInserer[['Date','id_joueur']].rename(columns={'Date':'date_choix'}).assign(saison=self.saison).to_sql('joueurs_choisis', c.sqlAlchemyConn, 'ttfl', if_exists='append', index=False)
        
        
class PasDeMatchError(Exception):  
    """
    erreur levee si pas de match à une date donnee
    """ 
    def __init__(self, dateJournee):
        self.dateJournee=dateJournee
        
    def __str__(self): 
        return "Pas de match le: %s" % self.dateJournee