# -*- coding: utf-8 -*-
'''
Created on 26 janv. 2021

@author: Martin
module de televersement dans  la bdd des donnees relative a une journee du site
'''

import pandas as pd
from TelechargementDonnees import JourneeSiteNba
import Connexion_Transfert as ct


class JourneeBdd(JourneeSiteNba) : 
    """
    un objet permettant les échanges entre la base et une journee telechargee
    """
    def __init__(self, dateJournee, bdd='basket', id_saison=1, id_type_match=0, id_type_playoffs=None) : 
        """
        attributes :
            dateJournee : string de date au format YYYY-mm-dd; attribut classe mere
            id_type_match : integer (saison reguliere=0 ou playoffs=1) ou dico avec en cle l'identifiant du match et en value le type de match
            id_type_playoffs : None pour saison reguliere, ou integer si tous les types de match sont les memes, ou un dico avec en cle l'identifiant du match et en value le type de match playoffs
            nouveauxJoueurs : list of string des joueurs qui n'etaient pas dans la liste avant
            joueursBlesses : list des joueurs qui sont noté nouvellements blesses
            chagementContrat : list des changement de contrat
        """
        super().__init__(dateJournee)
        self.bdd=bdd
        self.id_saison=id_saison
        self.id_type_match=id_type_match
        self.id_type_playoffs=id_type_playoffs
        self.dfMatchs,self.dfScoreMatch,self.dfNewContrat,self.dfContratJoueurChange=None,None, None, None
        self.dfNouveauBlesse,self.dfJoueurRetourBlessure,self.dfStatsJoueurs=None, None, None
     
    def creerAttributsGlobaux(self):
        """
        faire appel aux fonctions en dessous pour obtenir les attributs descriptifs de la journee
        """ 
        dfJoueursBdd, dfContratBdd, dfJoueursBlessesBdd=self.telechargerDonnees()
        self.verifJoueursInconnu(dfJoueursBdd)
        if not self.dfJoueursInconnus.empty : 
            dfJoueursBdd=self.ajoutJoueursInconnus()
        for k,v in self.dicoJournee.items() : 
            self.creerDfMatch(v['match'])
            idMatchBdd=self.recupererIdMatch()
            self.creerDfScoreMatch(v['match'],idMatchBdd)
            for e,s in enumerate((v['stats_e0'], v['stats_e1'])) : 
                #synthese et epuration des donnees de joueurs
                idEquipe=v['match'].loc[e].equipe
                dfJoueurActifBlesses=self.clearJoueursInactifs(s)
                dfJoueursTot=self.creerDfJoueurFinale(dfJoueurActifBlesses,dfJoueursBdd)
                #contrats
                self.contratJoueursinconnus(dfJoueursTot,dfContratBdd,idEquipe)
                self.modifContrats
                #blessures
                self.blessures(dfJoueursTot,dfJoueursBlessesBdd)
                self.retourBlessures(dfJoueursTot,dfJoueursBlessesBdd)
                #stats joueurs
                self.creerStatsJoueurs(dfJoueursTot,idMatchBdd)
       
    def telechargerDonnees(self) : 
        """
        recuperer la table des joueurs, contrat, blesses
        """
        with ct.ConnexionBdd(self.bdd) as c:
            dfJoueursBdd=pd.read_sql('select id_joueur, nom_simple from donnees_source.joueur',c.sqlAlchemyConn)
            dfContratBdd=pd.read_sql("SELECT * FROM donnees_source.contrat WHERE date_fin_contrat IS null",c.sqlAlchemyConn)
            dfJoueursBlessesBdd=pd.read_sql("select * from donnees_source.blessure WHERE date_guerison IS NULL",c.sqlAlchemyConn)
        return dfJoueursBdd, dfContratBdd, dfJoueursBlessesBdd
    
    def verifJoueursInconnu(self,dfJoueursBdd):
        """
        Trouver les joueurs de la journee non presents dans la base de donnees
        """
        dfJoueurJournee=pd.concat([v for c in self.dicoJournee.keys() for k,v in self.dicoJournee[c].items() if k[:6]!='match' ]).merge(dfJoueursBdd, on='nom_simple', how='left') 
        self.dfJoueursInconnus=dfJoueurJournee.loc[dfJoueurJournee.id_joueur.isna()][['nom','nom_simple']]
    
    def ajoutJoueursInconnus(self):
        """
        ajouter les joueurs inconnus à la base et retelecharger les donnees de joueurs
        """
        with ct.ConnexionBdd(self.bdd) as c:
            self.dfJoueursInconnus.to_sql('joueur', c.sqlAlchemyConn, schema='donnees_source', if_exists='append', index=False)  
            dfJoueursBdd=pd.read_sql('select id_joueur, nom_simple from donnees_source.joueur',c.sqlAlchemyConn)
        return dfJoueursBdd
        
    def creerDfMatch(self, dfMatch):
        """
        mettre en forme la df d'un match telechargee
        """
        equipeExt=dfMatch.iloc[0].equipe
        equipeDom=dfMatch.iloc[1].equipe
        self.dfMatchs=pd.concat([self.dfMatchs,pd.DataFrame({'id_saison':[self.id_saison],
                        'date_match':[self.dateJournee],'equipe_domicile':[equipeDom],
                        'equipe_exterieure':[equipeExt],'id_type_match':[self.id_type_match]})])
        
    def recupererIdMatch(self) :
        """
        obtenir l'id du Match en cours de transfert
        """
        with ct.ConnexionBdd(self.bdd) as c:
            idMatchBdd=c.sqlAlchemyConn.execute("SELECT last_value FROM donnees_source.match_id_match_seq").fetchone()[0]
        return idMatchBdd
    
    def creerDfScoreMatch(self,dfMatch,idMatchBdd) : 
        """
        creer la df des scores par periode
        in : 
            dfMatch :df du match issue du dicoJournee
            idMatchBdd : identifiant uniq du match dans la bdd, cf recupererIdMatch(
        """
        dfScoreMatch=dfMatch.melt(id_vars=['equipe'], value_vars=[c for c in dfMatch.columns if c !='equipe'],
                            var_name='id_periode', value_name='score_periode').sort_values('equipe')
        dfScoreMatch['id_match']=idMatchBdd
        self.dfScoreMatch=pd.concat([self.dfScoreMatch,dfScoreMatch])
        
    def clearJoueursInactifs(self,dfStatsJoueurs) : 
        return dfStatsJoueurs.loc[(~dfStatsJoueurs['dnp']) | dfStatsJoueurs['blesse']].copy()
    
    def creerDfJoueurFinale(self, dfJoueurActifBlesses,dfJoueursBdd):
        return dfJoueurActifBlesses.merge(dfJoueursBdd, on='nom_simple', how='left')
        
    def contratJoueursinconnus(self,dfJoueursTot,dfContratBdd,idEquipe) : 
        """
        ajouter une ligne dans la table des contrats si le joueurs n'y était pas
        in : 
            dfJoueursTot : df des joueurs actif ou blesses, mis a jour avec les nouveaux joueurs
            dfContratBdd : df des contrats connus dans la Bdd
            idEquipe : integer : id de l'equipe de laBdd (character varying (3))
        """
        dfJoueurSansContrat=dfJoueursTot.loc[~dfJoueursTot.id_joueur.isin(dfContratBdd.id_joueur.tolist())]
        if not dfJoueurSansContrat.empty : #joueur sans contrat
            self.dfNewContrat=pd.concat([self.dfNewContrat,pd.DataFrame({'id_joueur':dfJoueurSansContrat.id_joueur.tolist(),
                                                                         'id_equipe':idEquipe,'date_debut_contrat':self.dateJournee})])
            #dfNewContrat.to_sql('contrat',self.sqlAlchemyConn, schema='donnees_source', if_exists='append', index=False)
    
    def modifContrats(self,dfJoueursTot,dfContratBdd,idEquipe):
        """
        ajout date de fin pour contrat existant et insertion de la nouvelle ligne du nouveau contrat
        in : 
            dfJoueursTot : df des joueurs actif ou blesses, mis a jour avec les nouveaux joueurs
            dfContratBdd : df des contrats connus dans la Bdd
            idEquipe : integer : id de l'equipe de laBdd (character varying (3))
        """
        #2.joueur avec contrat : 
        #jointure entre la table contratBdd et celle du match sur id_joueur pour comparer les equipes
        if not dfContratBdd.empty : 
            dfContratJoueurMatch=dfContratBdd.merge(dfJoueursTot[['id_joueur']], on='id_joueur')
            dfContratJoueurChange=dfContratJoueurMatch.loc[dfContratJoueurMatch.id_equipe!=idEquipe]
            if not dfContratJoueurChange.empty: #si un joueur a changé d'équipe
                dateFinContrat=(pd.to_datetime(self.dateJournee)-pd.Timedelta(1,'day')).strftime('%Y-%m-%d')
                print(dfContratJoueurChange.id_joueur, dateFinContrat)
                #il faut update la table avec la valeur de date en date_fin_contrat
                #self.sqlAlchemyConn.execute(f"UPDATE donnees_source.contrat SET date_fin_contrat = '{dateFinContrat}' WHERE id_contrat=any(array{dfContratJoueurChange.id_contrat.tolist()})")
                #et inserer de nouvelle lignes
                self.dfNewContrat=pd.concat([self.dfNewContrat,pd.DataFrame({'id_joueur':dfContratJoueurChange.id_joueur.tolist(),
                                                                             'id_equipe':idEquipe,'date_debut_contrat':self.dateJournee})])
                self.dfContratJoueurChange=pd.concat([dfContratJoueurChange,self.dfContratJoueurChange])
                #dfNewContrat.to_sql('contrat',self.sqlAlchemyConn, schema='donnees_source', if_exists='append', index=False)
            
    def blessures(self, dfJoueursTot,dfJoueursBlessesBdd):
        """
        ajouter les joueurs blesses dansl la table des blessures
        ajout date de fin pour contrat existant et insertion de la nouvelle ligne du nouveau contrat
        in : 
            dfJoueursTot : df des joueurs actif ou blesses, mis a jour avec les nouveaux joueurs
            dfJoueursBlessesBdd : df des joueurs blesses dans la Bdd
        """
        #checker si des joueurs sont notés blessé et ne sont pas déjà dans la base blessure
        dfJoueursBlesses=dfJoueursTot.loc[dfJoueursTot['blesse']]
        if not dfJoueursBlesses.empty : #si des joueurs blesses, verifier qu'ils ne sont pas déjà presents dans la base
            dfNouveauBlesse=dfJoueursBlesses.loc[~dfJoueursBlesses.id_joueur.isin(dfJoueursBlessesBdd.id_joueur.tolist())]
            if not dfNouveauBlesse.empty : 
                dfNouveauBlesse=dfNouveauBlesse[['id_joueur']].assign(date_blessure=self.dateJournee, id_type_blessure=99)
                #dfNouveauBlesse.to_sql('blessure', self.sqlAlchemyConn, schema='donnees_source', if_exists='append', index=False)  
                self.dfNouveauBlesse=pd.concat([self.dfNouveauBlesse,dfNouveauBlesse])
        
    def retourBlessures(self,dfJoueursTot,dfJoueursBlessesBdd) : 
        """
        pour les joueurs qui jouent, vérifier s'ils n'étaient pas blesses et modifier
        in : 
            dfJoueursTot : df des joueurs actif ou blesses, mis a jour avec les nouveaux joueurs
            dfJoueursBlessesBdd : df des joueurs blesses dans la Bdd
        """
        #checker si des joueurs ayant joué étaient noté blessé mais sont revenus
        dfJoueurRetourBlessure=dfJoueursTot.loc[(dfJoueursTot.id_joueur.isin(dfJoueursBlessesBdd.id_joueur.tolist())) & (~dfJoueursTot['blesse'])]
        if not dfJoueurRetourBlessure.empty : #si des retours
            #dateGuerison=(pd.to_datetime(self.dateJournee)-pd.Timedelta(1,'day')).strftime('%Y-%m-%d')
            #il faut update la table avec la valeur de date en date_fin_blessurre
            #c.sqlAlchemyConn.execute(f"UPDATE donnees_source.blessure SET date_guerison = '{dateGuerison}' WHERE id_joueur=any(array{dfJoueurRetourBlessure.id_joueur.tolist()}) AND date_guerison is null")
            self.dfJoueurRetourBlessure=pd.concat([dfJoueurRetourBlessure, self.dfJoueurRetourBlessure])
    
    def creerStatsJoueurs(self,dfJoueursTot,idMatchBdd):
        """
        ajouter les stats des joueurs de chaque match a la df correspondante
        """
        dfStatsJoueurs=dfJoueursTot.loc[~dfJoueursTot['dnp']][['minute', 'points', 'rebonds', 'passes_dec', 'steal',
                       'contres', 'tir_reussi', 'tir_tentes', 'pct_tir', 'trois_pt_r',
                       'trois_pt_t', 'pct_3_pt', 'lanc_frc_r', 'lanc_frc_t', 'pct_lfrc',
                       'rebonds_o', 'rebonds_d', 'ball_perdu', 'faute_p', 'plus_moins','score_ttfl', 'id_joueur']].copy()
        dfStatsJoueurs['id_match']=idMatchBdd
        self.dfStatsJoueurs=pd.concat([self.dfStatsJoueurs,dfStatsJoueurs])
        #dfStatsJoueursBdd.to_sql('stats_joueur', c.sqlAlchemyConn, schema='donnees_source', if_exists='append', index=False)
        
        
    def exporterVersBdd(self,listExport):
        """
        exporter les dfs ciblées vers la Bdd
        in : 
            listExport : list de string decrivant les attribut, ou 'all' pour tout.
                         string possibles : dfMatchs, dfScoreMatch, dfNewContrat, 
                                            dfContratJoueurChange, dfNouveauBlesse, dfJoueurRetourBlessure
                                            dfStatsJoueurs
        """