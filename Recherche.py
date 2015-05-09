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