# -*- coding: utf-8 -*-
'''
Created on 20 nov. 2021

@author: Martin

Module contenant les parametres d'identifiaction des objets Web
'''

#################################################
################### SITE NBA ####################
#################################################
urlSiteNbaScore = 'https://www.nba.com/games'
classLienMatch_calendrier = "//a[@class='GameCard_gcm__SKtfh GameCardMatchup_gameCardMatchup__H0uPe']"
idBoutonGererCookieNba = "//button[@id='onetrust-accept-btn-handler']"
boutonGererCookieTtfl = "//button[@class='sd-cmp-JnaLO']/span[@class='sd-cmp-16t61 sd-cmp-2JYyd sd-cmp-3cRQ2']"
divDrapeauIncrustation = "//div[@class='ab-page-blocker']"
boutonCloseIncrustation = "//button[@class='ab-close-button']"
boutonCloseConnexionNba = "//div[@class='mvpd-modal-close-button']"
divTestCalendrier = "//div[@class='ab-in-app-message  ab-background ab-modal-interactions graphic ab-clickable ab-modal ab-centered']"
testTextPasDeMatch = "// *[contains(text(),\'No scheduled games')]"

#################################################
################### JOUEURS #####################
#################################################
urlPageJoueurs = 'https://www.nba.com/players'
listeDeroulanteNbPage = 'Page Number Selection Drown Down List'
classeTableauColonne1 = 'primary text RosterRow_primaryCol__19xPQ'
classeLienNom = 'flex items-center t6 Anchor_complexLink__2NtkO'
refDivCarac = 'PlayerSummary_playerInfo__1L8sx'
refParagrapheCarac = 'PlayerSummary_playerInfoValue__mSfou'
refElementNom = 'flex flex-col text-white'
sliderHistorique = 'Toggle_slider__hCMQQ'

