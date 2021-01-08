/* ==================================
 * CREER LA STRUCTURE DE BASE
 ====================================*/

-- DROP SCHEMA donnees_source;

CREATE SCHEMA donnees_source AUTHORIZATION postgres;

DROP TABLE IF EXISTS donnees_source.equipe;
DROP TABLE IF EXISTS donnees_source.joueur;
DROP TABLE IF EXISTS donnees_source.contrat;
DROP TABLE IF EXISTS donnees_source.match;
DROP TABLE IF EXISTS donnees_source.stats_joueur;
DROP TABLE IF EXISTS donnees_source.score_match;
DROP TABLE IF EXISTS donnees_source.enum_periode_match;
DROP TABLE IF EXISTS donnees_source.enum_type_match;
DROP TABLE IF EXISTS donnees_source.enum_type_playoffs;
DROP TABLE IF EXISTS donnees_source.enum_type_blessure;
DROP TABLE IF EXISTS donnees_source.enum_position_terrain;
DROP TABLE IF EXISTS donnees_source.enum_type_contrat;
DROP TABLE IF EXISTS donnees_source.blessure;
DROP TABLE IF EXISTS donnees_source.saison;


CREATE TABLE donnees_source.equipe (
    id_equipe VARCHAR(3) NOT NULL,
    nom_equipe VARCHAR NOT NULL,
    conference VARCHAR(5) NOT NULL,
	division VARCHAR NOT NULL ,
    PRIMARY KEY (id_equipe)
);

CREATE TABLE donnees_source.joueur (
    id_joueur SERIAL NOT NULL,
    date_naissance DATE,
    date_entree_nba DATE,
    date_sortie_nba DATE,
    nom VARCHAR NOT NULL,
    taille NUMERIC(3,2),
    poids NUMERIC (4,1),
    id_position_terrain VARCHAR NOT NULL,
    PRIMARY KEY (id_joueur)
);

CREATE TABLE donnees_source.contrat (
    id_contrat SERIAL NOT NULL,
    id_equipe VARCHAR(3) NOT NULL,
    id_joueur INTEGER NOT NULL,
    annee DATE NOT NULL,
    date_fin_contrat DATE,
    id_type_contrat INTEGER NOT NULL,
    montant_contrat INTEGER,
    PRIMARY KEY (id_contrat)
);

CREATE TABLE donnees_source.match (
    id_match SERIAL NOT NULL,
	id_saison INTEGER NOT NULL,
    date_match DATE NOT NULL,
    equipe_domicile VARCHAR(3) NOT NULL,
    equipe_exterieure VARCHAR(3) NOT NULL,
    id_type_match INTEGER NOT NULL,
    id_type_playoff INTEGER NOT NULL,
    PRIMARY KEY (id_match)
);

CREATE TABLE donnees_source.stats_joueur (
    id_stats_joueurs SERIAL NOT NULL,
    id_match BIGINT NOT NULL,
    id_joueur INTEGER NOT NULL,
    minute INTERVAL NOT NULL,
    points INTEGER NOT NULL,
    rebonds INTEGER NOT NULL,
    passes_dec INTEGER NOT NULL,
    steal INTEGER NOT NULL,
    contres INTEGER NOT NULL,
    tir_reussi INTEGER NOT NULL,
    tir_tentes INTEGER NOT NULL,
    pct_tir NUMERIC(5,2) NOT NULL,
    trois_pt_r INTEGER NOT NULL,
    trois_pt_t INTEGER NOT NULL,
    pct_3_pt NUMERIC(5,2) NOT NULL,
    lanc_frc_r INTEGER NOT NULL,
    lanc_frc_t INTEGER NOT NULL,
    pct_lfrc NUMERIC(5,2) NOT NULL,
    rebonds_o INTEGER NOT NULL,
    rebonds_d INTEGER NOT NULL,
    ball_perdu INTEGER NOT NULL,
    faute_p INTEGER NOT NULL,
    plus_moins NUMERIC(3,0) NOT NULL,
    score_ttfl INTEGER NOT NULL,
    PRIMARY KEY (id_stats_joueurs)
);

CREATE TABLE donnees_source.score_match (
    id_score_match BIGINT NOT NULL,
    id_match BIGINT NOT NULL,
    id_equipe VARCHAR(3) NOT NULL,
    id_periode VARCHAR NOT NULL,
    PRIMARY KEY (id_score_match)
);

CREATE TABLE donnees_source.enum_periode_match (
    id_periode VARCHAR NOT NULL,
    nom_periode VARCHAR NOT NULL,
    PRIMARY KEY (id_periode)
);

CREATE TABLE donnees_source.enum_type_match (
    id_type_match SERIAL NOT NULL,
    nom_type_match VARCHAR NOT NULL,
    PRIMARY KEY (id_type_match)
);

CREATE TABLE donnees_source.enum_type_playoffs (
    id_type_playoffs SERIAL NOT NULL,
    nom_type_playoffs VARCHAR NOT NULL,
    PRIMARY KEY (id_type_playoffs)
);

CREATE TABLE donnees_source.enum_type_blessure (
    id_type_blessure SERIAL NOT NULL,
    nom_blessure VARCHAR NOT NULL,
    PRIMARY KEY (id_type_blessure)
);

CREATE TABLE donnees_source.enum_position_terrain (
    id_position_terrain VARCHAR NOT NULL,
    nom_position_terrain VARCHAR NOT NULL,
    PRIMARY KEY (id_position_terrain)
);

CREATE TABLE donnees_source.enum_type_contrat (
    id_type_contrat INTEGER NOT NULL,
    nom_type_contrat VARCHAR NOT NULL,
    PRIMARY KEY (id_type_contrat)
);

CREATE TABLE donnees_source.blessure (
    id_blessure SERIAL NOT NULL,
    id_type_blessure INTEGER NOT NULL,
    id_joueur BIGINT NOT NULL,
    date_blessure DATE NOT NULL,
    date_guerison DATE ,
    PRIMARY KEY (id_blessure)
);

CREATE TABLE donnees_source.saison (
    id_saison SERIAL NOT NULL,
    date_debut DATE NOT NULL,
    date_fin DATE ,
	nom_saison VARCHAR,
    PRIMARY KEY (id_saison)
);

ALTER TABLE donnees_source.joueur ADD FOREIGN KEY (id_position_terrain) REFERENCES donnees_source.enum_position_terrain(id_position_terrain) ON UPDATE CASCADE;
ALTER TABLE donnees_source.contrat ADD FOREIGN KEY (id_equipe) REFERENCES donnees_source.equipe(id_equipe) ON UPDATE CASCADE;
ALTER TABLE donnees_source.contrat ADD FOREIGN KEY (id_joueur) REFERENCES donnees_source.joueur(id_joueur)ON UPDATE CASCADE;
ALTER TABLE donnees_source.contrat ADD FOREIGN KEY (id_type_contrat) REFERENCES donnees_source.enum_type_contrat(id_type_contrat) ON UPDATE CASCADE;
ALTER TABLE donnees_source.match ADD FOREIGN KEY (id_saison) REFERENCES donnees_source.saison(id_saison) ON UPDATE CASCADE;
ALTER TABLE donnees_source.match ADD FOREIGN KEY (equipe_domicile) REFERENCES donnees_source.equipe(id_equipe) ON UPDATE CASCADE;
ALTER TABLE donnees_source.match ADD FOREIGN KEY (equipe_exterieure) REFERENCES donnees_source.equipe(id_equipe) ON UPDATE CASCADE;
ALTER TABLE donnees_source.match ADD FOREIGN KEY (id_type_match) REFERENCES donnees_source.enum_type_match(id_type_match) ON UPDATE CASCADE;
ALTER TABLE donnees_source.match ADD FOREIGN KEY (id_type_playoff) REFERENCES donnees_source.enum_type_playoffs(id_type_playoffs) ON UPDATE CASCADE;
ALTER TABLE donnees_source.stats_joueur ADD FOREIGN KEY (id_joueur) REFERENCES donnees_source.joueur(id_joueur) ON UPDATE CASCADE;
ALTER TABLE donnees_source.stats_joueur ADD FOREIGN KEY (id_match) REFERENCES donnees_source.match(id_match) ON UPDATE CASCADE;
ALTER TABLE donnees_source.score_match ADD FOREIGN KEY (id_match) REFERENCES donnees_source.match(id_match) ON UPDATE CASCADE;
ALTER TABLE donnees_source.score_match ADD FOREIGN KEY (id_equipe) REFERENCES donnees_source.equipe(id_equipe) ON UPDATE CASCADE;
ALTER TABLE donnees_source.score_match ADD FOREIGN KEY (id_periode) REFERENCES donnees_source.enum_periode_match(id_periode) ON UPDATE CASCADE;
ALTER TABLE donnees_source.blessure ADD FOREIGN KEY (id_joueur) REFERENCES donnees_source.joueur(id_joueur) ON UPDATE CASCADE;
ALTER TABLE donnees_source.blessure ADD FOREIGN KEY (id_type_blessure) REFERENCES donnees_source.enum_type_blessure(id_type_blessure) ON UPDATE CASCADE;

/* ==================================
 * REMPLIR LES TABLES D'ENUMERATIONS
 ====================================*/
 
--remplir la table d'enumeration des types de periode de match
INSERT INTO donnees_source.enum_periode_match (id_periode, nom_periode)
 VALUES ('q1', '1er quart-temp'),
 		('q2', '2eme quart-temp'),
 		('q3', '3eme quart-temp'),
 		('q4', '4eme quart-temp'),
 		('pr1', 'prolongation 1'),
 		('pr2', 'prolongation 2'),
 		('pr3', 'prolongation 3'),
 		('pr4', 'prolongation 4'),
 		('pr5', 'prolongation 5'),
 		('final', 'score total') ;

--remplir la table d'enumeration des types de blessure
INSERT INTO donnees_source.enum_type_blessure (id_type_blessure, nom_blessure)
 VALUES (0, 'inconnue'),
		(1, 'ligaments croise genou') ;
		
--remplir la table d'enumeration des types de contrat
INSERT INTO donnees_source.enum_type_contrat (id_type_contrat, nom_type_contrat)
 VALUES (0, 'Qualifying Offer'),
 		(1, 'Non-Garanties'),
 		(2, 'Team Option'),
 		(3, 'Player Option'),
 		(4, 'Absent de l’équipe'),
 		(5, 'Early Termination Option (ETO)'),
 		(6, 'Contrat garanti') ;
		
--remplir la table d'enumeration des types de match
INSERT INTO donnees_source.enum_type_match (id_type_match, nom_type_match)
 VALUES (0, 'Saison Reguliere'),
 		(1, 'Playoffs') ;
		
--remplir la table d'enumeration des types de match
INSERT INTO donnees_source.enum_type_playoffs (id_type_playoffs, nom_type_playoffs)
 VALUES (0, 'premier tour'),
 		(1, 'demi finale conference'),
 		(2, 'finale conference'),
 		(3, 'finale NBA') ;
		
/*=======================================
 * REMPLIR LES TABLES JOUEURS ET EQUIPES
 =======================================*/
 
 -- les tables joueurs et equipe sont initialisées dans le notebook TransfertBdd.ipynb
 
 /*=======================================
 * REMPLIR LA TABLE SAISON
 =======================================*/
 INSERT INTO donnees_source.saison(date_debut, nom_saison) 
 values('2020-12-22', '2020-2021')
 