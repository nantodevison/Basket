/* ==================================
 * CREER LA STRUCTURE DE BASE
 ====================================*/

-- DROP SCHEMA donnees_source;

CREATE SCHEMA donnees_source AUTHORIZATION postgres;
CREATE SCHEMA ttfl AUTHORIZATION postgres;

DROP TABLE IF EXISTS donnees_source.equipe;
DROP TABLE IF EXISTS donnees_source.stats_equipes;
DROP TABLE IF EXISTS donnees_source.joueur;
DROP TABLE IF EXISTS donnees_source.contrat;
DROP TABLE IF EXISTS donnees_source."match";
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

--TTFL
CREATE TABLE ttfl.joueurs_choisis (
 id_joueur_choisis SERIAL PRIMARY KEY,
 id_joueur integer REFERENCES donnees_source.joueur (id_joueur) ON UPDATE CASCADE,
 date_choix date,
 id_saison REFERENCES donnees_source.saison (id_saison) ON UPDATE CASCADE) ;
ALTER TABLE ttfl.joueurs_choisis ADD CONSTRAINT ttfl_joueurs_choisi_unique UNIQUE (id_joueur, date_choix);
 

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
 		(4, 'Absent de lâ€™Ã©quipe'),
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
 
 -- les tables joueurs et equipe sont initialisÃ©es dans le notebook TransfertBdd.ipynb
 
 /*=======================================
 * REMPLIR LA TABLE SAISON
 =======================================*/
 INSERT INTO donnees_source.saison(date_debut, nom_saison) 
 values('2020-12-22', '2020-2021') ;
 
 /* ========================
  * REMPLIR LA TABLE BLESSURE
  =========================*/
  
 --exemple de remplissage Ã  la main
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

--recuperer les noms de joueurs blesse dont la date de debut de blessure est antÃ©rieure Ã  une date et qui n'ont pas guÃ©ri 
select b.*,j.nom from donnees_source.joueur j JOIN donnees_source.blessure b ON j.id_joueur=b.id_joueur ;

/*==============================
 * RECUPERER LE CONTRAT LE PLUS RECENT
 ===============================* 
 */

SELECT DISTINCT ON (id_joueur) id_equipe, id_joueur, date_debut_contrat
 FROM donnees_source.contrat
 ORDER BY id_joueur, date_debut_contrat DESC
 

 
/*================================================
 *VUE DE CALCUL DES OFFENSIVE ET DEFENSIVE RATINGS 
 ==================================================*/
  
-- c'est un calcul par match, basé sur le nombre de possessions
--cf https://www.basketball-reference.com/about/ratings.html

--calcul du nombre de possession : 
	-- d'abord les stats cumulees par equipes et par match
CREATE OR REPLACE VIEW donnees_source.stats_joueurs_match AS 
SELECT j.id_joueur, j.nom, j.nom_simple, d.id_match, c.id_equipe, d."minute", d.points, d.rebonds, d.passes_dec, d.steal, d.contres, d.tir_reussi, 
d.tir_tentes, d.pct_tir, d.trois_pt_r, d.trois_pt_t, d.pct_3_pt, d.lanc_frc_r, d.lanc_frc_t, d.pct_lfrc, 
d.rebonds_o, d.rebonds_d, d.ball_perdu, d.faute_p, d.plus_moins, d.score_ttfl
 FROM  (SELECT sj.id_joueur, sj.id_match, m.date_match, sj."minute", sj.points, sj.rebonds, sj.passes_dec, sj.steal, sj.contres, sj.tir_reussi, sj.tir_tentes, sj.pct_tir, sj.trois_pt_r, sj.trois_pt_t, sj.
pct_3_pt, sj.lanc_frc_r, sj.lanc_frc_t, sj.pct_lfrc, sj.rebonds_o, sj.rebonds_d, sj.ball_perdu, sj.faute_p, sj.plus_moins, sj.score_ttfl
	     FROM donnees_source.stats_joueur sj JOIN donnees_source."match" m ON sj.id_match=m.id_match) d 
	     JOIN donnees_source.contrat c ON (c.id_joueur=d.id_joueur AND (
										     d.date_match BETWEEN c.date_debut_contrat AND c.date_fin_contrat OR (
										     d.date_match >= c.date_debut_contrat AND c.date_fin_contrat IS NULL) ))
	     JOIN donnees_source.joueur j ON j.id_joueur = d.id_joueur
	     
	-- calcul des stats cumulees par equipe et par match
CREATE OR REPLACE VIEW donnees_source.stats_cumul_eqp_match AS 
SELECT id_equipe, id_match, sum("minute") minutes, sum(points) points, sum(rebonds) rebonds, sum(passes_dec) passes_dec, sum(steal) steal, 
       sum(contres) contres, sum(tir_reussi) tir_reussi, sum(tir_tentes) tir_tentes,  (sum(tir_reussi)::NUMERIC/sum(tir_tentes)*100)::NUMERIC(5,2) pct_tir, 
       sum(trois_pt_r) trois_pt_r, sum(trois_pt_t) trois_pt_t,  (sum(trois_pt_r)::NUMERIC/sum(trois_pt_t)*100)::numeric(5,2) pct_3_pt, sum(lanc_frc_r) lanc_frc_r, 
       sum(lanc_frc_t) lanc_frc_t,  (sum(lanc_frc_r)::numeric/sum(lanc_frc_t)*100)::numeric(5,2) pct_lfrc, sum(rebonds_o) rebonds_o, sum(rebonds_d) rebonds_d, 
       sum(ball_perdu) ball_perdu, sum(faute_p) faute_p
  FROM donnees_source.stats_joueurs_match
  GROUP BY id_match, id_equipe
  
  	--on verifie que l'on a bien que 2 equipes par id_match dans la vue des stats cumulee
SELECT id_match, count(id_match)
  FROM donnees_source.stats_cumul_eqp_match
  GROUP BY id_match
  HAVING count(id_match) != 2

	--calcul des stats avancees par match
CREATE OR REPLACE VIEW donnees_source.stats_avancee_match AS 
WITH 
nb_poss AS (
SELECT id_equipe, id_match, points, minutes,
 donnees_source.func_nb_possessions(tir_tentes,rebonds_o,ball_perdu,lanc_frc_t) possessions
 FROM donnees_source.stats_cumul_eqp_match)
SELECT *,
       CASE WHEN row_number() OVER w = 1 THEN (lead(points) OVER w / possessions*100)::NUMERIC(5,2)
       ELSE (lag(points) OVER w / LAG(possessions) OVER w*100)::NUMERIC(5,2)
       END team_def_rating, 
       (points/possessions*100)::NUMERIC(5,2) team_off_rating,
       CASE WHEN row_number() OVER w = 1 THEN donnees_source.func_pace(LEAD(possessions) OVER w,possessions,round(EXTRACT(EPOCH FROM minutes)/60)::integer)
           ELSE donnees_source.func_pace(LAG(possessions) OVER w,possessions,round(EXTRACT(EPOCH FROM minutes)/60)::integer) 
           END pace,
       CASE WHEN row_number() OVER w = 1 THEN lead(points) OVER w 
               ELSE lag(points) OVER w
               END points_encaisse       
 FROM nb_poss
 WINDOW w AS (PARTITION BY id_match)
 ORDER BY id_match
 
 	--calcul des stats avance par saison
CREATE OR REPLACE VIEW donnees_source.stats_cumul_eqp_saison AS 
SELECT id_equipe, sum("minutes") minutes, avg(points)::numeric(5,2) points, avg(rebonds)::numeric(3,1) rebonds, avg(passes_dec)::numeric(3,1) passes_dec, avg(steal)::numeric(2,1) steal, 
       avg(contres)::numeric(3,1) contres, avg(tir_reussi)::numeric(5,2) tir_reussi, avg(tir_tentes)::numeric(5,2) tir_tentes,  (sum(tir_reussi)::NUMERIC/sum(tir_tentes)*100)::NUMERIC(5,2) pct_tir, 
       avg(trois_pt_r)::numeric(5,2) trois_pt_r, avg(trois_pt_t)::numeric(5,2) trois_pt_t,   (sum(trois_pt_r)::NUMERIC/sum(trois_pt_t)*100)::numeric(5,2) pct_3_pt, avg(lanc_frc_r)::numeric(5,2) lanc_frc_r, 
       avg(lanc_frc_t)::numeric(5,2) lanc_frc_t,   (sum(lanc_frc_r)::numeric/sum(lanc_frc_t)*100)::numeric(5,2) pct_lfrc, avg(rebonds_o)::numeric(3,1) rebonds_o, avg(rebonds_d)::numeric(3,1) rebonds_d, 
       avg(ball_perdu)::numeric(3,1) ball_perdu, avg(faute_p)::numeric(3,1) faute_p
  FROM donnees_source.stats_cumul_eqp_match 
  GROUP BY id_equipe
  
CREATE OR REPLACE VIEW donnees_source.stats_avancee_saison AS 
WITH
stats_match AS (
SELECT * ,
          CASE WHEN row_number() OVER w = 1 THEN lead(possessions) OVER w 
               ELSE lag(possessions) OVER w
               END possessions_opp
 FROM donnees_source.stats_avancee_match
 WINDOW w AS (PARTITION BY id_match))
SELECT id_equipe, (sum(points)/sum(possessions)*100)::numeric(5,2) team_off_rating, 
       avg(points)::numeric(5,2) points_moy,
       (sum(points_encaisse)/sum(possessions_opp)*100)::numeric(5,2) team_def_rating, 
       avg(points_encaisse)::numeric(5,2) points_encaisse_moy,
       avg(pace)::numeric(5,2) pace
 FROM stats_match
 GROUP BY id_equipe

 
--classements
SELECT *, ROW_NUMBER() OVER (ORDER BY team_off_rating DESC) off_rtg_rank,
          ROW_NUMBER() OVER (ORDER BY points_moy DESC) points_marq_rank,
          ROW_NUMBER() OVER (ORDER BY team_def_rating) def_rtg_rank,
          ROW_NUMBER() OVER (ORDER BY points_encaisse_moy) points_encaisse_rank
 FROM donnees_source.stats_avancee_saison
 
/* ========================
 * FONCTIONS
 ====================== */
 
--calcul du nombre de possessions
CREATE OR REPLACE FUNCTION donnees_source.func_nb_possessions (IN tir_tentes bigint, rebonds_o bigint, ball_perdu bigint, lanc_frc_t bigint,
                        OUT possessions numeric)
LANGUAGE plpgsql
AS
$$
BEGIN 
	possessions=0.96*(tir_tentes - rebonds_o + ball_perdu +(0.44*lanc_frc_t)) ;
END 
$$ ;
COMMENT ON FUNCTION donnees_source.func_nb_possessions(bigint,bigint,bigint,bigint) IS 'calcul du nombre de possesions
par equipe et par match' ;


-- fonction de calcul de la pace
CREATE OR REPLACE FUNCTION donnees_source.func_pace (IN team_poss numeric, opp_poss numeric, team_minutes integer,
                        OUT pace NUMERIC)
LANGUAGE plpgsql
AS
$$
BEGIN 
	pace=48*((team_poss+opp_poss)/(2*(team_minutes/5))) ;
END 
$$ ;
COMMENT ON FUNCTION donnees_source.func_pace(numeric,numeric,integer) IS 'calcul du nombre de possesions
moyen (peu importe le temps de match) par equipe et par match' ;

-- supression à partir d'une date
CREATE OR REPLACE FUNCTION donnees_source.supprimer_par_date(dateMin date)
RETURNS VOID
LANGUAGE plpgsql
AS
$$

BEGIN 
DELETE FROM donnees_source.score_match
WHERE id_match IN (
SELECT id_match 
 FROM donnees_source."match"
 WHERE date_match >= dateMin) ;
DELETE FROM donnees_source.stats_equipes
WHERE id_match IN (
SELECT id_match 
 FROM donnees_source."match"
 WHERE date_match >= dateMin) ;
DELETE FROM donnees_source.stats_joueur
WHERE id_match IN (
SELECT id_match 
 FROM donnees_source."match"
 WHERE date_match >= dateMin) ;
DELETE FROM donnees_source."match"
WHERE id_match IN (
SELECT id_match 
 FROM donnees_source."match"
 WHERE date_match >= dateMin) ;
DELETE FROM donnees_source.blessure
WHERE date_blessure >= dateMin;
DELETE FROM donnees_source.contrat
WHERE date_debut_contrat >= dateMin;
END
$$ ;
COMMENT ON FUNCTION donnees_source.supprimer_par_date(date) IS 'supprmier des tables match, blessures, contrat, stats_joueur, stat_equipe, score match les
données de date supéreiure ou égale à la date en entrée' ;

--selection des x derniers match des joueurs
CREATE OR REPLACE FUNCTION donnees_source.x_dernier_match(nb_match integer)
RETURNS TABLE (id_joueur integer, nom CHARACTER VARYING , nom_simple CHARACTER VARYING, id_match int8, id_equipe CHARACTER VARYING (3), "minute" interval, points integer, 
                rebonds integer, passes_dec integer, steal integer, contres integer, tir_reussi integer, tir_tentes integer, pct_tir numeric(5,2), trois_pt_r integer, trois_pt_t integer, 
                pct_3_pt numeric(5,2), lanc_frc_r integer, lanc_frc_t integer, pct_lfrc numeric(5,2), rebonds_o integer, rebonds_d integer, ball_perdu integer, faute_p integer,
                plus_moins NUMERIC(3), score_ttfl integer, num_match int8, date_match date )
LANGUAGE plpgsql
AS 
$$
BEGIN
    RETURN QUERY 
    SELECT * 
     FROM (SELECT sj.*, ROW_NUMBER() OVER (PARTITION BY sj.id_joueur ORDER BY m.date_match desc) numero_match, m.date_match
            FROM donnees_source.stats_joueurs_match sj JOIN donnees_source."match" m ON m.id_match=sj.id_match) t
     WHERE numero_match<=5 ;
END
$$ ;
COMMENT ON FUNCTION donnees_source.x_dernier_match(integer) IS 'renvoyer une table pareille à celle de donnees_source.stats_joueurs_match avec seulement les x dernier matchs de chaque joueur'

--selection des x meileurs joueurs sur les y dernier matchs
CREATE OR REPLACE FUNCTION ttfl.x_meilleurs_ttfl_x_match(nb_match integer, nb_joueurs integer)
RETURNS TABLE (id_joueur integer, score_ttfl_moy numeric(4,1) )
LANGUAGE plpgsql
AS 
$$ 
BEGIN 
    RETURN QUERY
    SELECT t.id_joueur, avg(t.score_ttfl) score_ttfl_moy
        FROM (SELECT * FROM donnees_source.x_dernier_match(nb_match:=nb_match)) t
        GROUP BY t.id_joueur
        ORDER BY score_ttfl_moy DESC
        LIMIT nb_joueurs ;
END 
$$ ; 
COMMENT ON FUNCTION ttfl.x_meilleurs_ttfl_x_match(integer, integer) IS 'renvoyer la liste des x joueurs avec la meilleure moyenne ttfl sur les y dernier matchs de chaque joueur'

--selection des x meileurs joueurs sur les y dernier matchs avec prise en compte disponibilite blessure et ttfl
CREATE OR REPLACE FUNCTION ttfl.x_meilleurs_ttfl_x_match_dispo(nb_match integer, nb_joueurs integer, date_ref date)
RETURNS TABLE (id_joueur integer, nom CHARACTER VARYING , nom_simple CHARACTER VARYING, id_match int8, id_equipe CHARACTER VARYING (3), "minute" interval, points integer, 
                rebonds integer, passes_dec integer, steal integer, contres integer, tir_reussi integer, tir_tentes integer, pct_tir numeric(5,2), trois_pt_r integer, trois_pt_t integer, 
                pct_3_pt numeric(5,2), lanc_frc_r integer, lanc_frc_t integer, pct_lfrc numeric(5,2), rebonds_o integer, rebonds_d integer, ball_perdu integer, faute_p integer,
                plus_moins NUMERIC(3), score_ttfl integer, num_match int8, date_match date, score_ttfl_moy NUMERIC(4,1), type_indispo CHARACTER VARYING)
LANGUAGE plpgsql
AS 
$$ 
BEGIN 
     RETURN QUERY
     WITH 
        ttfl_choix_recent_joueur AS (
        SELECT DISTINCT ON (id_joueur) *
         FROM ttfl.joueurs_choisis
         ORDER BY id_joueur, date_choix DESC),
        ttfl_joueur_dispo AS (
         SELECT *
          FROM ttfl_choix_recent_joueur
          WHERE date_choix > (date_ref - 30)),
        joueurs_a_filtrer AS (
        SELECT t.id_joueur,'choix_ttfl'::CHARACTER VARYING type_indisponibilite FROM ttfl_joueur_dispo t 
         UNION 
        SELECT b.id_joueur, 'blesse'::CHARACTER VARYING type_indisponibilite FROM donnees_source.blessure b WHERE date_guerison IS NULL),
        suppr_doublon_blessure_choix_ttfl AS (
        SELECT DISTINCT ON (d.id_joueur, d.date_match) d.*, l.score_ttfl_moy, f.type_indisponibilite
         FROM donnees_source.x_dernier_match(nb_match:=5) d JOIN 
              (SELECT * FROM ttfl.x_meilleurs_ttfl_x_match(nb_match:=nb_match, nb_joueurs:=nb_joueurs)) l ON d.id_joueur=l.id_joueur
              LEFT JOIN joueurs_a_filtrer f  ON d.id_joueur=f.id_joueur
         ORDER BY d.id_joueur, d.date_match, f.type_indisponibilite) 
        SELECT s.*
         FROM suppr_doublon_blessure_choix_ttfl s
         ORDER BY s.score_ttfl_moy DESC,s.id_joueur, s.type_indisponibilite ;    
END
$$ ;
COMMENT ON function ttfl.x_meilleurs_ttfl_x_match_dispo(integer, integer, date) IS 'renvoyer la liste des x joueurs avec la meilleure moyenne ttfl sur les y dernier matchs de chaque joueur, avec la dispo 
selon les blessure et les choi ttfl'


/* ======================================================================
 * exemple de suppression de l''intégralité des données postérieure à une date
 ======================================================================= */
SELECT donnees_source.supprimer_par_date('2021-02-24')

/*===================================================================
 * Vue des 30 meilleusr joueurs ttfl sur les 5 derniers matchs, avec dispo selon blessure et ttfl
 ====================================================================*/

-- vue de base, sans prise en compte des données de joueurs deja pris ou blesses
CREATE OR REPLACE VIEW ttfl.bestjoueurs_matchrecents AS 
select * FROM ttfl.x_meilleurs_ttfl_x_match_dispo(5,30,(SELECT CURRENT_DATE))
 
--en prenant en compte les joueurs pris ou blesses
WITH 
ttfl_choix_recent_joueur AS (
SELECT DISTINCT ON (id_joueur) *
 FROM ttfl.joueurs_choisis
 ORDER BY id_joueur, date_choix DESC),
ttfl_joueur_dispo AS (
 SELECT *
  FROM ttfl_choix_recent_joueur
  WHERE date_choix > (SELECT CURRENT_DATE - 30)),
joueurs_a_filtrer AS (
SELECT id_joueur,'choix_ttfl' type_indispo FROM ttfl_joueur_dispo 
 UNION 
SELECT id_joueur, 'blesse' type_indispo FROM donnees_source.blessure WHERE date_guerison IS NULL)
SELECT d.*, l.score_ttfl_moy, f.type_indispo
 FROM donnees_source.x_dernier_match(nb_match:=5) d JOIN 
      (SELECT * FROM donnees_source.x_meilleurs_ttfl_x_match(nb_match:=5, nb_joueurs:=20)) l ON d.id_joueur=l.id_joueur
      LEFT JOIN joueurs_a_filtrer f  ON d.id_joueur=f.id_joueur
 ORDER BY score_ttfl_moy DESC










  
  
  
 