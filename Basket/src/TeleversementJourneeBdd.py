# -*- coding: utf-8 -*-
'''
Created on 26 janv. 2021

@author: Martin
module de televersement dans  la bdd des donnees relative a une journee du site
'''

import pandas as pd
from datetime import date
from TelechargementDonnees import JourneeSiteNba, Blessures
import Connexion_Transfert as ct

def miseAJourBlessesBdd(dfInjuries,sqlAlchemyConn):
    """
    mettre à jour les blesses de la Bdd qui presente un id_type_blessure à 99
    et qui sont sur le site de CBS dans les blesses
    in :
        sqlAlchemyConn : connexion sqlAlchemy à la base
        dfInjuries : dataframe des blesses issu de la classe Blessures du module TelechargementDonnees
    """
    rqtBlesseEnCoursBdd="""SELECT b.id_blessure, j.nom, j.nom_simple
                             FROM donnees_source.blessure b JOIN donnees_source.joueur j ON b.id_joueur=j.id_joueur
                             WHERE date_guerison IS NULL and id_type_blessure=99"""
    blesseEnCoursBdd=pd.read_sql(rqtBlesseEnCoursBdd, sqlAlchemyConn)
    #creer la df finale de MaJ
    tempDfBlessePourMaJ=blesseEnCoursBdd.merge(dfInjuries, on='nom_simple')
    #insrere cette df dans la base
    if not tempDfBlessePourMaJ.empty : 
        tempDfBlessePourMaJ.to_sql('blesses_temp', sqlAlchemyConn, schema='public', if_exists='replace', index=False)
        #update la table
        rqtUpdate="""UPDATE donnees_source.blessure b
                      SET id_type_blessure=t.id_type_blessure
                      FROM public.blesses_temp t
                      WHERE b.id_blessure=t.id_blessure"""
        sqlAlchemyConn.execute(rqtUpdate)
        #drop la table temporaire
        sqlAlchemyConn.execute("DROP TABLE IF EXISTS public.blesses_temp")

def insererBlessesInconnusMatchBefore(dfInjuries,sqlAlchemyConn):
    """
    insrere dans la bdd les blesses non repertories dans les feuilles de matchs, mais qui ont daje joue
    un match avant (i.e qu'on retrouve dans la table des stats joueurs)
    in : 
        sqlAlchemyConn : connexion sqlAlchemy à la base
        dfInjuries : dataframe des blesses issu de la classe Blessures du module TelechargementDonnees
    """
    rqtBlesseEnCoursBdd="""SELECT b.id_blessure, j.nom, j.nom_simple
                             FROM donnees_source.blessure b JOIN donnees_source.joueur j ON b.id_joueur=j.id_joueur
                             WHERE date_guerison IS NULL and id_type_blessure!=99"""
    blesseEnCoursBdd=pd.read_sql(rqtBlesseEnCoursBdd, sqlAlchemyConn)
    dfInjuriesInconnu=dfInjuries.loc[~dfInjuries.nom_simple.isin(blesseEnCoursBdd.nom_simple.tolist())]
    dfInjuriesInconnu.to_sql('blesses_inconnus_temp', sqlAlchemyConn, schema='public', if_exists='replace', index=False)
    rqtBlessesInconnusAInserer="""WITH 
                                tous_matchs_blesses_inconnus as(
                                SELECT *
                                 FROM public.blesses_inconnus_temp bi JOIN (SELECT s.*, m.date_match
                                      FROM donnees_source.stats_joueurs_match s JOIN donnees_source."match" m ON s.id_match=m.id_match) s 
                                      ON s.nom_simple=bi.nom_simple),
                                blesses_inconnus_dernier_match AS (
                                SELECT DISTINCT ON (id_joueur) id_joueur, "Injury", date_match, date_match+1 date_blessure
                                 FROM tous_matchs_blesses_inconnus
                                 ORDER BY id_joueur, date_match DESC),
                                blesses_inconnus_insertion as(
                                SELECT b.id_joueur,b.date_blessure,e.id_type_blessure
                                 FROM blesses_inconnus_dernier_match b JOIN donnees_source.enum_type_blessure e ON b."Injury"=lower(e.nom_blessure_anglais))
                                INSERT INTO donnees_source.blessure (id_joueur, date_blessure, id_type_blessure)
                                 SELECT id_joueur, date_blessure, id_type_blessure FROM blesses_inconnus_insertion"""
    sqlAlchemyConn.execute(rqtBlessesInconnusAInserer)
    sqlAlchemyConn.execute("DROP TABLE IF EXISTS public.blesses_inconnus_temp")
    
def insererBlessesInconnusPasMatchBefore(dfInjuries,sqlAlchemyConn):
    """
    insrere dans la bdd les blesses non repertories dans les feuilles de matchs, 
    et qui n'ont pas joue de matchs avant (i.e non reêrtorie dans table stats_joueurs)
    in : 
        sqlAlchemyConn : connexion sqlAlchemy à la base
        dfInjuries : dataframe des blesses issu de la classe Blessures du module TelechargementDonnees
    """
    rqtBlesseEnCoursBdd="""SELECT b.id_blessure, j.nom, j.nom_simple
                             FROM donnees_source.blessure b JOIN donnees_source.joueur j ON b.id_joueur=j.id_joueur
                             WHERE date_guerison IS NULL and id_type_blessure!=99"""
    blesseEnCoursBdd=pd.read_sql(rqtBlesseEnCoursBdd, sqlAlchemyConn)
    joueurs=pd.read_sql('select nom_simple, id_joueur from donnees_source.joueur', sqlAlchemyConn)
    dfInjuriesInconnu=dfInjuries.loc[~dfInjuries.nom_simple.isin(blesseEnCoursBdd.nom_simple.tolist())].merge(
                        joueurs, on='nom_simple')
    dfInjuriesInconnu['date_blessure']=dfInjuriesInconnu.Updated.apply(lambda x : pd.to_datetime(' '.join(x.split(', ')[1].split()
                                                                                    [::-1]+[str(date.today().year),])))
    dfInjuriesInconnu[['id_joueur','date_blessure','id_type_blessure']].to_sql('blessure', sqlAlchemyConn, 
                                                                    schema='donnees_source', if_exists='append', index=False)
    
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
        self.dfNouveauBlesse,self.dfJoueurRetourBlessure,self.dfStatsJoueurs,self.dfStatsEquipes=None, None, None, None
     
    def creerAttributsGlobaux(self):
        """
        faire appel aux fonctions en dessous pour obtenir les attributs descriptifs de la journee
        """ 
        dfJoueursBdd, dfContratBdd, dfJoueursBlessesBdd=self.telechargerDonnees()
        self.verifJoueursInconnu(dfJoueursBdd)
        if not self.dfJoueursInconnus.empty : 
            dfJoueursBdd=self.ajoutJoueursInconnus()
        idMatchMaxBdd=self.recupererIdMatch()
        self.modifCleDico(idMatchMaxBdd)
        for k,v in self.dicoJournee.items() : 
            self.creerDfMatch(v['match'], k)
            self.creerDfScoreMatch(v['match'],k)
            self.creerDfStatsEquipes(v['stats_equipes'],k)
            for e,s in enumerate((v['stats_e0'], v['stats_e1'])) : 
                #synthese et epuration des donnees de joueurs
                idEquipe=v['match'].loc[e].id_equipe
                dfJoueurActifBlesses=self.clearJoueursInactifs(s)
                dfJoueursTot=self.creerDfJoueurFinale(dfJoueurActifBlesses,dfJoueursBdd)
                #contrats
                self.contratJoueursinconnus(dfJoueursTot,dfContratBdd,idEquipe)
                self.modifContrats(dfJoueursTot,dfContratBdd,idEquipe)
                #blessures
                self.blessures(dfJoueursTot,dfJoueursBlessesBdd)
                self.retourBlessures(dfJoueursTot,dfJoueursBlessesBdd)
                #stats joueurs
                self.creerStatsJoueurs(dfJoueursTot,k)
       
    def telechargerDonnees(self) : 
        """
        recuperer la table des joueurs, contrat, blesses
        """
        with ct.ConnexionBdd(self.bdd) as c:
            dfJoueursBdd=pd.read_sql('select id_joueur, nom_simple from donnees_source.joueur',c.sqlAlchemyConn)
            dfContratBdd=pd.read_sql("SELECT * FROM donnees_source.contrat WHERE date_fin_contrat IS null",c.sqlAlchemyConn)
            dfJoueursBlessesBdd=pd.read_sql("select * from donnees_source.blessure WHERE date_guerison IS NULL",c.sqlAlchemyConn)
        return dfJoueursBdd, dfContratBdd, dfJoueursBlessesBdd
    
    def recupererIdMatch(self) :
        """
        obtenir l'id du Match en cours de transfert
        """
        with ct.ConnexionBdd(self.bdd) as c:
            idMatchBdd=c.sqlAlchemyConn.execute('SELECT max(id_match) FROM donnees_source."match"').fetchone()[0]
        return idMatchBdd
    
    def modifCleDico(self, idMatchMaxBdd):
        """
        modfier le dioJournee pour remplacer la cle par la valeur de id_match
        in :
            idMatchMaxBdd : integer : max de l'id_match dans la bdd
        """
        self.dicoJournee={k+idMatchMaxBdd+1:v for k,v in self.dicoJournee.items()}
    
    def verifJoueursInconnu(self,dfJoueursBdd):
        """
        Trouver les joueurs de la journee non presents dans la base de donnees
        """
        dfJoueurJournee=pd.concat([v for c in self.dicoJournee.keys() for k,v in self.dicoJournee[c].items() if k in ('stats_e0', 'stats_e1') ]).merge(dfJoueursBdd, on='nom_simple', how='left') 
        self.dfJoueursInconnus=dfJoueurJournee.loc[dfJoueurJournee.id_joueur.isna()][['nom','nom_simple']]
    
    def ajoutJoueursInconnus(self):
        """
        ajouter les joueurs inconnus à la base et retelecharger les donnees de joueurs
        """
        with ct.ConnexionBdd(self.bdd) as c:
            self.dfJoueursInconnus.to_sql('joueur', c.sqlAlchemyConn, schema='donnees_source', if_exists='append', index=False)  
            dfJoueursBdd=pd.read_sql('select id_joueur, nom_simple from donnees_source.joueur',c.sqlAlchemyConn)
        return dfJoueursBdd
        
    def creerDfMatch(self, dfMatch, id_match):
        """
        mettre en forme la df d'un match telechargee
        in : 
            dfMatch : df des equipes du match 
            id_match : identiifant du match
        """
        equipeExt=dfMatch.iloc[0].id_equipe
        equipeDom=dfMatch.iloc[1].id_equipe
        self.dfMatchs=pd.concat([self.dfMatchs,pd.DataFrame({'id_match':id_match,'id_saison':[self.id_saison],
                        'date_match':[self.dateJournee],'equipe_domicile':[equipeDom],
                        'equipe_exterieure':[equipeExt],'id_type_match':[self.id_type_match]})])
        
    def creerDfStatsEquipes(self, dfStatsEquipes, id_match):
        """
        mettre en forme la df des stats générales par equipes 'points dans l apeinture, points du banc,
        etc...
        in : 
            dfStatsEquipes :df ddes stats par equipes issue du dicoJournee
            id_match : identifiant du match concernes
        """
        dfStatsEquipes['id_match']=id_match
        self.dfStatsEquipes=pd.concat([self.dfStatsEquipes,dfStatsEquipes])
        
    
    def creerDfScoreMatch(self,dfMatch,idMatchBdd) : 
        """
        creer la df des scores par periode
        in : 
            dfMatch :df du match issue du dicoJournee
            idMatchBdd : identifiant uniq du match dans la bdd, cf recupererIdMatch(
        """
        dfScoreMatch=dfMatch.melt(id_vars=['id_equipe'], value_vars=[c for c in dfMatch.columns if c !='id_equipe'],
                            var_name='id_periode', value_name='score_periode').sort_values('id_equipe')
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
    
    def modifContrats(self,dfJoueursTot,dfContratBdd,idEquipe):
        """
        ajout date de fin pour contrat existant et insertion de la nouvelle ligne du nouveau contrat
        in : 
            dfJoueursTot : df des joueurs actif ou blesses, mis a jour avec les nouveaux joueurs
            dfContratBdd : df des contrats connus dans la Bdd
            idEquipe : integer : id de l'equipe de laBdd (character varying (3))
        """
        #jointure entre la table contratBdd et celle du match sur id_joueur pour comparer les equipes
        if not dfContratBdd.empty : 
            dfContratJoueurMatch=dfContratBdd.merge(dfJoueursTot[['id_joueur']], on='id_joueur')
            dfContratJoueurChange=dfContratJoueurMatch.loc[dfContratJoueurMatch.id_equipe!=idEquipe]
            if not dfContratJoueurChange.empty: #si un joueur a changé d'équipe
                self.dfNewContrat=pd.concat([self.dfNewContrat,pd.DataFrame({'id_joueur':dfContratJoueurChange.id_joueur.tolist(),
                                                                             'id_equipe':idEquipe,'date_debut_contrat':self.dateJournee})])
                self.dfContratJoueurChange=pd.concat([dfContratJoueurChange,self.dfContratJoueurChange])
            
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
        #passage du timedelta en string pour import dans bdd ensuite
        dfStatsJoueurs['minute']=dfStatsJoueurs.minute.apply(
            lambda x: f'{x.components.hours:02d}:{x.components.minutes:02d}:{x.components.seconds:02d}'
                      if not pd.isnull(x) else '')
        self.dfStatsJoueurs=pd.concat([self.dfStatsJoueurs,dfStatsJoueurs])        
        
    def exporterVersBdd(self,bdd='basket',listExport='all'):
        """
        exporter les dfs ciblées vers la Bdd
        in : 
            bdd : string : raccourci de connexion vers la Bdd
            listExport : list de string decrivant les attribut, ou 'all' pour tout.
                         string possibles : match, contrat, blesse, stats
        """
        dateVeille=(pd.to_datetime(self.dateJournee)-pd.Timedelta(1,'day')).strftime('%Y-%m-%d')
        with ct.ConnexionBdd(bdd) as c :
            if 'match' in listExport or listExport=='all':
                self.dfMatchs.to_sql('match', c.sqlAlchemyConn, schema='donnees_source', if_exists='append', index=False)
                self.dfScoreMatch.to_sql('score_match', c.sqlAlchemyConn, schema='donnees_source', if_exists='append', index=False)
                self.dfStatsEquipes.to_sql('stats_equipes',c.sqlAlchemyConn, schema='donnees_source', if_exists='append', index=False)
            if 'contrat' in listExport or listExport=='all':
                if isinstance(self.dfNewContrat, pd.DataFrame) and not self.dfNewContrat.empty :
                    self.dfNewContrat.to_sql('contrat',c.sqlAlchemyConn, schema='donnees_source', if_exists='append', index=False)
                if isinstance(self.dfContratJoueurChange, pd.DataFrame) and not self.dfContratJoueurChange.empty :
                    c.sqlAlchemyConn.execute(f"UPDATE donnees_source.contrat SET date_fin_contrat = '{dateVeille}' WHERE id_contrat=any(array{self.dfContratJoueurChange.id_contrat.tolist()})")
            if 'blesse' in listExport or listExport=='all':
                #dans un premier temps on insere les blesses
                if isinstance(self.dfNouveauBlesse, pd.DataFrame) and not self.dfNouveauBlesse.empty  :
                    self.dfNouveauBlesse.to_sql('blessure', c.sqlAlchemyConn, schema='donnees_source', if_exists='append', index=False)
                if isinstance(self.dfJoueurRetourBlessure, pd.DataFrame) and not self.dfJoueurRetourBlessure.empty :
                    c.sqlAlchemyConn.execute(f"UPDATE donnees_source.blessure SET date_guerison = '{dateVeille}' WHERE id_joueur=any(array{self.dfJoueurRetourBlessure.id_joueur.tolist()}) AND date_guerison is null")
                #puis on met a jour les type de blessures
                if isinstance(self.dfInjuries, pd.DataFrame) and not self.dfInjuries.empty :
                    miseAJourBlessesBdd(self.dfInjuries,c.sqlAlchemyConn)
                    insererBlessesInconnusMatchBefore(self.dfInjuries,c.sqlAlchemyConn)
                    insererBlessesInconnusPasMatchBefore(self.dfInjuries,c.sqlAlchemyConn)
            if 'stats' in listExport or listExport=='all':
                self.dfStatsJoueurs.to_sql('stats_joueur', c.sqlAlchemyConn, schema='donnees_source', if_exists='append', index=False)
        