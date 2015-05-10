import Authentification

__author__ = 'Harmore'

import time
from DB_Models import Tache

from handler import Handler
import hashlib
import re
from DB_Models import Utilisateur

class Recherche(Handler) :
    def render_font(self, recherche="", erreur=""):
        self.render("Recherche.html", recherche=recherche, erreur=erreur)

    def get(self):
        self.render("Recherche.html")

    def post(self):
        recherche=self.request.get('recherche')
        type=self.request.get('type')

        if not recherche :
            self.render_font(erreur="Veuillez entrer un critere de recherche ou retournez sur l'accueil")

        else :
            error=""
            if type=="Ville":
                taches=Tache.getTacheByVille(str(recherche.upper()))
                if not taches :
                    error="Aucun resultat (Pas de sensibilite a la casse)"
            else :
                taches=Tache.getTacheByUsername(str(recherche))
                if not taches :
                    error="Aucun resultat (Sensibilite a la casse)"

            self.render("Recherche.html", recherche=recherche, taches=taches, erreur=error)

class PagePerso(Handler):
    def get(self):
        cookie=self.request.cookies.get("user_info")
        self.write(cookie)
        if cookie:
            if Authentification.validCookie(cookie) is None:
                values=cookie.split(":")
                user=Utilisateur.getUtilisateur(str(values[0].split('=')[1].split('|')[0]), update=True)
                if user:
                    TacheUser = Tache.getTaches()
                    self.render("Utilisateur.html",utilisateur=user,TacheUser=TacheUser)
                else :
                    self.render("Utilisateur.html")
        else:
            self.render("Utilisateur.html")
