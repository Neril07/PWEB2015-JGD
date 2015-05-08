__author__ = 'Harmore'

from google.appengine.ext import db
from google.appengine.api import memcache

#@param: key represente l'id de la tache voulue ou "tous" si jamais on veut toutes les taches
#@param: update indique si il faut mettre a jour le cache
def getTache(key,update=False):
    tache=memcache.get("E"+key)
    if tache is None or update:
        if key=="tous":
            tache=db.GqlQuery("SELECT * FROM tache ORDER BY titre ASC").fetch(limit=None)
            memcache.set("T"+key,tache)
        else:
            tache=db.GqlQuery("SELECT * FROM Tache WHERE id= '%s'"%key).fetch(limit=1)
            if tache:
                tache=tache[0]
                setTache(tache)
    return tache

#@param: tache represente le modele ci dessous complete
def setTache(tache):
    memcache.set("T"+tache.id,tache)

# pour recuperer la liste de toutes les taches
def getTaches(update=False):
    taches = memcache.get('taches')
    if (not taches) or update:
        taches = db.GqlQuery("SELECT * FROM Tache ORDER BY titre")
        memcache.set('taches', taches)
    return taches


def getTacheByUsername(user):
    tache = db.GqlQuery("SELECT * FROM Tache WHERE user = '%s'" % user).fetch(limit=None)
    return tache

def getTacheByVille(ville):
    tache = db.GqlQuery("SELECT * FROM Tache WHERE ville = '%s'" % ville).fetch(limit=None)
    return tache

def suppTache(tache):
    tache.delete()


class Tache(db.Model):
    id=db.StringProperty(required=True)
    titre=db.StringProperty(required=True)
    user=db.StringProperty(required=True)
    ville=db.StringProperty(required=True)
    prix=db.IntegerProperty(default=None)
    participants=db.StringListProperty(default=None)