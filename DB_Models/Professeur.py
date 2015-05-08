#from Tix import _dummyButton

__author__ = 'svg'

from google.appengine.ext import db
from google.appengine.api import memcache

#@param: key represente l'id du professeur voulu
#@param: update indique si il faut mettre a jour le cache
def getProfesseur(key,update=False):
    professeur=memcache.get("P"+key)
    if professeur is None or update:
        if key=="tous":
            professeur=db.GqlQuery("SELECT * FROM Professeur ORDER BY nomPrenom ASC").fetch(limit=None)
            memcache.set("P"+key, professeur)
        else:
            professeur=db.GqlQuery("SELECT * FROM Professeur WHERE id='%s'"%key).fetch(limit=1)
            if professeur:
                professeur=professeur[0]
                setProfesseur(professeur)
    return professeur


#@param: professeur represente le model ci dessous complete
def setProfesseur(professeur):
    memcache.set(professeur.id,professeur)

def getProfesseurByName(nom):
    professeur = db.GqlQuery("SELECT * FROM Professeur WHERE nomPrenom = '%s'"%nom).fetch(limit=None)
    return professeur

class Professeur(db.Model):
    nomPrenom=db.StringProperty(required=True)
    id=db.StringProperty(required=True)