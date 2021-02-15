/* ==================================
 * CREER LA STRUCTURE DE BASE
 ====================================*/

-- DROP SCHEMA donnees_source;

CREATE SCHEMA donnees_source AUTHORIZATION postgres;

DROP TABLE IF EXISTS donnees_source.equipe;
DROP TABLE IF EXISTS donnees_source.stats_equipes;
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

CREATE TABLE donnees_source.stats_equipes (
	id_stats_equipes SERIAL NOT NULL,
	id_match integer NOT NULL REFERENCES donnees_source.match (id_match) ON UPDATE CASCADE,
    id_equipe VARCHAR(3) NOT NULL REFERENCES donnees_source.equipe (id_equipe) ON UPDATE CASCADE ,
	pts_in_paint INTEGER ,
	fastbreak_pts INTEGER,
	biggest_lead INTEGER,
    pts_banc INTEGER, 
	tm_rebonds INTEGER,
	ball_perdu INTEGER,
	tm_ball_perdu INTEGER,
	pt_subi_ctrattaq INTEGER,
    PRIMARY KEY (id_stats_equipes)
);
ALTER TABLE donnees_source.stats_equipes ADD CONSTRAINT stats_equipes_un UNIQUE (id_match,id_equipe);

CREATE TABLE donnees_source.joueur (
    id_joueur SERIAL NOT NULL,
    date_naissance DATE,
    date_entree_nba DATE,
    date_sortie_nba DATE,
    nom VARCHAR NOT NULL,
	nom_simple VARCHAR NOT NULL UNIQUE,
    taille NUMERIC(3,2),
    poids NUMERIC (4,1),
    id_position_terrain VARCHAR,
    PRIMARY KEY (id_joueur)
);

CREATE TABLE donnees_source.contrat (
    id_contrat SERIAL NOT NULL,
    id_equipe VARCHAR(3) NOT NULL,
    id_joueur INTEGER NOT NULL,
	date_debut_contrat DATE NOT NULL,
    date_fin_contrat DATE,
    id_type_contrat INTEGER,
    montant_contrat INTEGER,
    PRIMARY KEY (id_contrat)
);
ALTER TABLE donnees_source.contrat ADD CONSTRAINT contrat_unique UNIQUE (id_equipe, id_joueur, date_debut_contrat);

CREATE TABLE donnees_source.match (
    id_match INTEGER NOT NULL,
	id_saison INTEGER NOT NULL,
    date_match DATE NOT NULL,
    equipe_domicile VARCHAR(3) NOT NULL,
    equipe_exterieure VARCHAR(3) NOT NULL,
    id_type_match INTEGER NOT NULL,
    id_type_playoff INTEGER,
    PRIMARY KEY (id_match)
);
ALTER TABLE donnees_source."match" ADD CONSTRAINT match_unique UNIQUE (date_match, equipe_domicile, equipe_exterieure);

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
ALTER TABLE donnees_source.stats_joueur ADD CONSTRAINT stats_joueur_unique UNIQUE (id_match, id_joueur);

CREATE TABLE donnees_source.score_match (
    id_score_match SERIAL NOT NULL,
    id_match BIGINT NOT NULL,
    id_equipe VARCHAR(3) NOT NULL,
    id_periode VARCHAR NOT NULL,
	score_periode integer not null,
    PRIMARY KEY (id_score_match)
);
ALTER TABLE donnees_source.score_match ADD CONSTRAINT score_match_unique UNIQUE (id_match, id_equipe,id_periode);

CREATE TABLE donnees_source.enum_periode_match (
    id_periode VARCHAR NOT NULL,
    nom_periode VARCHAR NOT NULL,
    PRIMARY KEY (id_periode)
);

CREATE TABLE donnees_source.enum_type_match (
    id_type_match INTEGER NOT NULL,
    nom_type_match VARCHAR NOT NULL,
    PRIMARY KEY (id_type_match)
);

CREATE TABLE donnees_source.enum_type_playoffs (
    id_type_playoffs INTEGER NOT NULL,
    nom_type_playoffs VARCHAR NOT NULL,
    PRIMARY KEY (id_type_playoffs)
);

CREATE TABLE donnees_source.enum_type_blessure (
    id_type_blessure INTEGER NOT NULL,
    nom_blessure VARCHAR NOT NULL
	nom_blessure_anglais VARCHAR,
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
ALTER TABLE donnees_source.blessure ADD CONSTRAINT blessure_unique UNIQUE (id_joueur, date_blessure);

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
INSERT INTO donnees_source.enum_type_blessure (id_type_blessure, nom_blessure, nom_blessure_anglais)
 VALUES (0, 'inconnue', NULL),
		(1, 'ligaments croise genou', NULL),
		(2, 'entorse genou', NULL),
		(3, 'cheville', 'ankle'),
		(4, 'genou', 'knee'),
		(5,'poignet','wrist'),
		(6,'pied','foot'),
		(7,'hanche','hip'),
		(8,'mollet','calf'),
		(9,'talon d''achille','Achilles'),
		(10,'Cuisse','Quadriceps'),
		(11,'Abdomen','Abdomen'),
		(12,'jambe','lower leg'),
 		(13,'pouce','thumb'),
 		(14,'epaule','shoulder'),
 		(15,'aine','groin'),
 		(16,'Covid-19','Covid-19'),
 		(17,'repos','rest'),
 		(18,'claquage','Hamstring'),
 		(19,'maladie','Illness'),
		(20,'dos','Back'),
 		(21,'personel','Personal'),
 		(22,'comossion','Concussion'),
 		(23,'cuisse','Thigh'),
 		(24,'orteil','Toe'),
 		(25,'doigt','Finger'),
		(26,'jambe','Leg'),
		(27,'main','hand'),
		(99,'NC',NULL);
		
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
 values('2020-12-22', '2020-2021') ;
 
 /* ========================
  * REMPLIR LA TABLE BLESSURE
  =========================*/
  
 --exemple de remplissage à la main
INSERT INTO donnees_source.blessure  (id_joueur, id_type_blessure, date_blessure)
 SELECT id_joueur, 1,'2021-01-06' 
 FROM donnees_source.joueur j
 WHERE nom='Markelle Fultz' ;
 
INSERT INTO donnees_source.blessure  (id_joueur, id_type_blessure, date_blessure)
 SELECT id_joueur, 1,'2021-01-10' 
 FROM donnees_source.joueur j
 WHERE nom='Thomas Bryant' ;
 
INSERT INTO donnees_source.blessure  (id_joueur, id_type_blessure, date_blessure)
 SELECT id_joueur, 2,'2021-01-23' 
 FROM donnees_source.joueur j
 WHERE nom='Payton Pritchard' ;
 
--remplissage auto dans un des notebook, se basant sur les donnees de blesses de CBS SPORT, utilisant la requete suivante ( se base sur un travail precedent
--d'identification des blesses inconnus
WITH 
tous_matchs_blesses_inconnus as(
SELECT *
 FROM public.blesses_inconnus_temp bi JOIN (SELECT s.*, m.date_match
      FROM donnees_source.stat_nom s JOIN donnees_source."match" m ON s.id_match=m.id_match) s 
      ON s.nom_simple=bi.nom_simple),
blesses_inconnus_dernier_match AS (
SELECT DISTINCT ON (id_joueur) id_joueur, "Injury", date_match, date_match+1 date_blessure
 FROM tous_matchs_blesses_inconnus
 ORDER BY id_joueur, date_match DESC),
blesses_inconnus_insertion as(
SELECT b.id_joueur,b.date_blessure,e.id_type_blessure
 FROM blesses_inconnus_dernier_match b JOIN donnees_source.enum_type_blessure e ON b."Injury"=lower(e.nom_blessure_anglais))
INSERT INTO donnees_source.blessure (id_joueur, date_blessure, id_type_blessure)
 SELECT id_joueur, date_blessure, id_type_blessure FROM blesses_inconnus_insertion

 /* ========================
  * QUESTIONNER LA TABLE BLESSURE
  ========================= */

--recuperer les noms de joueurs blesse dont la date de debut de blessure est antérieure à une date et qui n'ont pas guéri 
select b.*,j.nom from donnees_source.joueur j JOIN donnees_source.blessure b ON j.id_joueur=b.id_joueur ;

/*==============================
 * RECUPERER LE CONTRAT LE PLUS RECENT
 ===============================* 
 */

SELECT DISTINCT ON (id_joueur) id_equipe, id_joueur, date_debut_contrat
 FROM donnees_source.contrat
 ORDER BY id_joueur, date_debut_contrat desc
 
/*==============================
 * VUES LES PLUS UTILES
 ===============================* 
 */
CREATE OR REPLACE VIEW donnees_source.stat_nom AS 
 SELECT s.*, j.nom, j.nom_simple
  FROM donnees_source.stats_joueur s JOIN donnees_source.joueur j ON j.id_joueur=s.id_joueur
 