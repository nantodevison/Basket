-- DROP SCHEMA donnees_source;

CREATE SCHEMA donnees_source AUTHORIZATION postgres;

DROP TABLE IF EXISTS equipe;
DROP TABLE IF EXISTS joueur;
DROP TABLE IF EXISTS contrat;
DROP TABLE IF EXISTS match;
DROP TABLE IF EXISTS stats_joueur;
DROP TABLE IF EXISTS score_match;
DROP TABLE IF EXISTS enum_periode_match;
DROP TABLE IF EXISTS enum_type_match;
DROP TABLE IF EXISTS enum_type_playoffs;
DROP TABLE IF EXISTS enum_type_blessure;
DROP TABLE IF EXISTS enum_position_terrain;
DROP TABLE IF EXISTS enum_type_contrat;

CREATE TABLE donnees_source.equipe (
    id_equipe INTEGER NOT NULL,
    nom_equipe VARCHAR NOT NULL,
    conference VARCHAR(5) NOT NULL,
    PRIMARY KEY (id_equipe)
);

CREATE TABLE donnees_source.joueur (
    id_joueur INTEGER NOT NULL,
    date_naissance DATE,
    date_entree_nba DATE,
    date_sortie_nba DATE,
    nom VARCHAR NOT NULL,
    taille NUMERIC,
    poids NUMERIC,
    blesse BOOLEAN NOT NULL,
    id_blessure INTEGER NOT NULL,
    id_position_terrain [VARCHAR] NOT NULL,
    PRIMARY KEY (id_joueur)
);

CREATE TABLE donnees_source.contrat (
    id_contrat BIGINT NOT NULL,
    id_equipe INTEGER NOT NULL,
    id_joueur INTEGER NOT NULL,
    annee DATE NOT NULL,
    date_fin_contrat DATE,
    type_contrat INTEGER NOT NULL,
    montant_contrat INTEGER,
    PRIMARY KEY (id_contrat)
);

CREATE TABLE donnees_source.match (
    id_match BIGINT NOT NULL,
    date_match DATE NOT NULL,
    equipe_domicile INTEGER NOT NULL,
    equipe_exterieure INTEGER NOT NULL,
    id_type_match INTEGER NOT NULL,
    id_type_playoff INTEGER NOT NULL,
    PRIMARY KEY (id_match)
);

CREATE TABLE donnees_source.stats_joueur (
    id_stats_joueurs INTEGER NOT NULL,
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
    pct_tir NUMERIC NOT NULL,
    trois_pt_r INTEGER NOT NULL,
    trois_pt_t INTEGER NOT NULL,
    pct_3_pt NUMERIC NOT NULL,
    lanc_frc_r INTEGER NOT NULL,
    lanc_frc_t INTEGER NOT NULL,
    pct_lfrc NUMERIC NOT NULL,
    rebonds_o INTEGER NOT NULL,
    rebonds_d INTEGER NOT NULL,
    ball_perdu INTEGER NOT NULL,
    faute_p INTEGER NOT NULL,
    plus_moins NUMERIC NOT NULL,
    score_ttfl INTEGER NOT NULL,
    PRIMARY KEY (id_stats_joueurs)
);

CREATE TABLE donnees_source.score_match (
    id_score_match BIGINT NOT NULL,
    id_match BIGINT NOT NULL,
    id_equipe INTEGER NOT NULL,
    id_periode INTEGER NOT NULL,
    PRIMARY KEY (id_score_match)
);

CREATE TABLE donnees_source.enum_periode_match (
    id_periode INTEGER NOT NULL,
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

ALTER TABLE donnees_source.joueur ADD FOREIGN KEY (id_blessure) REFERENCES donnees_source.enum_type_blessure(id_type_blessure);
ALTER TABLE donnees_source.joueur ADD FOREIGN KEY (id_position_terrain) REFERENCES donnees_source.enum_position_terrain(id_position_terrain);
ALTER TABLE donnees_source.contrat ADD FOREIGN KEY (id_equipe) REFERENCES donnees_source.equipe(id_equipe);
ALTER TABLE donnees_source.contrat ADD FOREIGN KEY (id_joueur) REFERENCES donnees_source.joueur(id_joueur);
ALTER TABLE donnees_source.contrat ADD FOREIGN KEY (type_contrat) REFERENCES donnees_source.enum_type_contrat(id_type_contrat);
ALTER TABLE donnees_source.match ADD FOREIGN KEY (equipe_domicile) REFERENCES donnees_source.equipe(id_equipe);
ALTER TABLE donnees_source.match ADD FOREIGN KEY (equipe_exterieure) REFERENCES donnees_source.equipe(id_equipe);
ALTER TABLE donnees_source.match ADD FOREIGN KEY (id_type_match) REFERENCES donnees_source.enum_type_match(id_type_match);
ALTER TABLE donnees_source.match ADD FOREIGN KEY (id_type_playoff) REFERENCES donnees_source.enum_type_playoffs(id_type_playoffs);
ALTER TABLE donnees_source.stats_joueur ADD FOREIGN KEY (id_joueur) REFERENCES donnees_source.joueur(id_joueur);
ALTER TABLE donnees_source.stats_joueur ADD FOREIGN KEY (id_match) REFERENCES donnees_source.match(id_match);
ALTER TABLE donnees_source.score_match ADD FOREIGN KEY (id_match) REFERENCES donnees_source.match(id_match);
ALTER TABLE donnees_source.score_match ADD FOREIGN KEY (id_equipe) REFERENCES donnees_source.equipe(id_equipe);
ALTER TABLE donnees_source.score_match ADD FOREIGN KEY (id_periode) REFERENCES donnees_source.enum_periode_match(id_periode);