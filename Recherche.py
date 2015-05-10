import Authentification

__author__ = 'Harmore'

import time
from DB_Models.Tache import Tache

from handler import Handler
import hashlib
import re
from DB_Models import Utilisateur

class Recherche(Handler) :
    def get(self):
        self.render("Recherche.html")

class PagePerso(Handler):
    def get(self):
        cookie=self.request.cookies.get("user_info")
        self.write(cookie)
        if cookie:
            if Authentification.validCookie(cookie) is None:
                values=cookie.split(":")
                user=Utilisateur.getUtilisateur(str(values[0].split('=')[1].split('|')[0]), update=True)
                if user:
                   self.render("Utilisateur.html",utilisateur=user)
                else :
                    self.render("Utilisateur.html")
        else:
            self.render("Utilisateur.html")
