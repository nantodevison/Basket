-- table de resume des stats pour les mathcs a venir d'une date predefinie
WITH 
-- récupérer la liste des jouers concernes par une date du calendrier
list_joueur AS (
 SELECT c.id_calendrier, c.id_saison, c.date_match, c.dom_ext, c2.id_equipe adversaire, e.*
  FROM donnees_source.calendrier_long_form c JOIN 
 	(SELECT * FROM  donnees_source.effectif_date(current_date, 'ALL')) e ON e.id_equipe=c.id_equipe
 	JOIN donnees_source.calendrier_long_form c2 ON c2.id_calendrier = c.id_calendrier AND c2.id_equipe != c.id_equipe
  WHERE c.date_match='2022-03-07'
  ORDER BY c.id_equipe),
-- recuperer tous les adversaires de toute les equipes avant cette date du caldendrier
list_adv_saison as(
 SELECT *, ROW_NUMBER() over(PARTITION BY id_equipe ORDER BY date_match desc) rank_match
  FROM donnees_source.x_dernier_matchs_all_eqp(2, -1)
  WHERE date_match<'2022-03-07'),
-- ne garder que les x derniers adversaires
last_adv as( 
 SELECT l.* 
  FROM list_adv_saison l
  WHERE l.rank_match <= 5),
-- trouver la saison concerneee par la date de reference
find_saison AS (
 SELECT s.id_saison --recuperer la saison
  FROM donnees_source.saison s
  WHERE '2022-03-07' BETWEEN s.date_debut AND s.date_fin OR '2022-03-07'>=s.date_debut AND s.date_fin IS NULL),
-- recuperer le classement complet de toute les equipes sur toute la saison jusqu'a la date de reference
classement_complet AS (
 SELECT *
  FROM classements.func_classement_equipes_complet_saison(2,'2022-03-07')),
-- recuperer le classement et le ration victoire-defaite sur les 10 derniers matchs, pour toutes les équipes 
classement_recent AS (  
 SELECT *, rank() OVER (ORDER BY pct_win desc) rang_10_matchs
  FROM donnees_source.func_victoire_defaite_date_nb_match('2022-03-07'::date, 10)),
-- recuperer le score TTFL des joueurs sur toute la saison
score_ttfl_joueurs AS (
 SELECT l.date_match, l.id_equipe, l.dom_ext, l.adversaire, t.id_joueur, t.nom, t.ttfl_median_tot, t.ttfl_moy_tot,t.min_ttfl_tot, t.max_ttfl_tot,
        ROW_NUMBER() OVER (PARTITION BY l.id_equipe ORDER BY t.ttfl_median_tot DESC) rang
  FROM list_joueur l JOIN ttfl.ttfl_par_equipe t ON t.id_joueur=l.id_joueur),
-- recuperer le score TTFL des joueurs sur les X derniers matchs
score_ttfl_joueurs_last_matchs AS (
SELECT id_joueur, nom, id_equipe, ttfl_moy_tot ttfl_moy_tot_last_matchs, ttfl_median_tot ttfl_median_tot_last_matchs, min_ttfl_tot min_ttfl_tot_last_matchs, 
       max_ttfl_tot max_ttfl_tot_last_matchs, last_matchs
 FROM ttfl.ttfl_equipe(2, 10)),
-- recuperer le def rating global sur la saison 
def_rating_saison AS (
 SELECT *
  FROM classements.classement_stats_avancees_equipe),
-- calcul du def rating sur les x derniers matchs trouvés avant
def_rating_last_match AS (
 SELECT l.id_equipe, sam.team_def_rating team_def_rating_last_match, l.adversaire, l.id_match
  FROM last_adv l JOIN donnees_source.stats_avancee_match sam ON sam.id_equipe = l.id_equipe AND sam.id_match = l.id_match), 
-- calcul du rang de classement du def rating sur les  x derniers matchs trouvés avant
rank_def_rating_last_match AS (
 SELECT id_equipe, avg(team_def_rating_last_match) def_rating_last_match_moy, ROW_NUMBER() OVER (ORDER  BY avg(team_def_rating_last_match)) def_rating_last_match_rank 
  FROM def_rating_last_match 
  GROUP BY id_equipe),
-- A VERIFIER regroupement des infos de chaque equipe : classement total, classement et resultats sur 10 derniers matchs, def_rating_global, def_rating_sur les 10 derniers matchs. 
-- Il faut une seule ligne par équipe
info_equipes AS (
SELECT distinct l.id_equipe, c.total_rank, c.conference_rank,
       r.def_rating_last_match_moy, r.def_rating_last_match_rank
 FROM last_adv l JOIN classement_complet c ON l.id_equipe = c.id_equipe
                   JOIN rank_def_rating_last_match r ON l.id_equipe = r.id_equipe),
-- A FAIRE : regrouper les données TTFL de chaque joueur, sur la saison et sur les 10 derniers matchs, avec les données de l'adersaire : classements et def ratings
fin as(
SELECT s.id_equipe, s.nom , s.ttfl_median_tot, s.ttfl_moy_tot, s.max_ttfl_tot, s.min_ttfl_tot, s.adversaire, i.total_rank adv_total_rank, i.conference_rank adv_conf_rank, i.def_rating_last_match_rank adv_def_rating_last_match, donnees_source.is_back2back(s.date_match, s.id_equipe), donnees_source.back2back_num_match(s.date_match, s.id_equipe),
       s.ttfl_median_tot - round((30-i.total_rank + i.def_rating_last_match_rank)/2) predict_ttfl
 FROM score_ttfl_joueurs s JOIN info_equipes i ON i.id_equipe=s.adversaire
                           --LEFT JOIN donnees_source.stats_joueur sj ON sj.id_match = i.id_match AND s.id_joueur = sj.id_joueur
 WHERE s.rang <= 5
 ORDER BY s.ttfl_median_tot DESC, s.nom, s.date_match DESC)
-- A FAIRE : tester des combinanison de calculs
SELECT id_equipe, team_def_rating, points_encaisse_moy, def_rtg_rank, points_encaisse_rank FROM def_rating_saison



