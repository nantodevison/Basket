# -*- coding: utf-8 -*-
'''
Created on 23 mars 2021

@author: Martin
regroupe les fonctions permettant de recuperer et inserer les vlauers par defaut dans la fenetre IHM a l'ouverture
'''

import pandas as pd
import Connexion_Transfert as ct
from datetime import timedelta, date

def lastDates(bdd='basket'):
    """
    recuperer dans la bdd la derniere date de match et la date la plus avancee de calendrier et l'identifiant de saison
    in : 
        bdd : string de connexion a la base
    out :
        dateMatchRecentBdd : date du dernier match stocke en bdd
        dateCalendrierRecent : date : date du calendreir la plus avancee
        dateMatchAImporter : date : date du 1er jour a importer pour completer la base des matchs
        dateCalendrierAImporter : date : date du 1er jour a importer pour completer la base du calendrier
    """
    with ct.ConnexionBdd(bdd) as c:
        resultDateMatchRecent=c.sqlAlchemyConn.execute('SELECT max(date_match) FROM donnees_source.match')
        resultDateCalendrierRecent=c.sqlAlchemyConn.execute('SELECT max(date_match), max(id_saison) FROM donnees_source.calendrier')
        dateMatchRecentBdd=resultDateMatchRecent.fetchone()[0]
        resultatsInter=resultDateCalendrierRecent.fetchall()[0]
        dateCalendrierRecent, idSaisonRecent=resultatsInter[0],resultatsInter[1]
    dateMatchAImporter=dateMatchRecentBdd + timedelta(days=1)
    dateCalendrierAImporter=dateCalendrierRecent + timedelta(days=1)
    return dateMatchRecentBdd, dateCalendrierRecent, dateMatchAImporter, dateCalendrierAImporter, idSaisonRecent

def nbJourneeImportDefaut(dateCalendrierAImporter):
    """
    calculer le nombre de jours à importer en fonction du dernier jour connu
    in : 
        dateCalendrierAImporter : date : premier jour a importer
    """
    nbJoursMatchs = (date.today() - dateCalendrierAImporter).days
    return nbJoursMatchs
        