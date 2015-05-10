
import json
from google.appengine.ext import db
from google.appengine.api import memcache

def tache_key(name = 'default'):
    return db.Key.from_path('taches', name)


#@param: key represente l'id de la tache voulue ou "tous" si jamais on veut toutes les taches
#@param: update indique si il faut mettre a jour le cache
def getTache(key,update=False):
    tache=memcache.get("E"+key)
    if tache is None or update:
        if key=="tous":
            tache=db.GqlQuery("SELECT * FROM tache ORDER BY date DESC").fetch(limit=None)
            memcache.set("T"+key,tache)
        else:
            key = db.Key.from_path('Tache', int(key), parent=tache_key(name = 'default'))
            tache = db.get(key)

    return tache

#@param: tache represente le modele ci dessous complete
def setTache(tache):
    memcache.set("T"+tache.id,tache)

# pour recuperer la liste de toutes les taches
def getTaches(update=False):
    taches = memcache.get('taches')
    if (not taches) or update:
        taches = db.GqlQuery("SELECT * FROM Tache ORDER BY date DESC")
        memcache.set('taches', taches)
    return taches


def getTacheByUsername(user):
    tache = db.GqlQuery("SELECT * FROM Tache WHERE user = '%s' ORDER BY date DESC" % user).fetch(limit=None)
    return tache

def getTacheByVille(ville):
    tache = db.GqlQuery("SELECT * FROM Tache WHERE ville = '%s' ORDER BY date DESC" % ville).fetch(limit=None)
    return tache

def suppTache(tache):
    tache.delete()


class Tache(db.Model):
    titre=db.StringProperty(required=True)
    user=db.StringProperty(required=True)
    ville=db.StringProperty(required=True)
    prix=db.IntegerProperty(default=None)
    participants=db.StringListProperty(default=None)
    date=db.DateTimeProperty(auto_now_add = True)
    desc = db.TextProperty(required=False)


def setTache(titre,ville,user,prix,desc):
    t = Tache(parent=tache_key(),titre=titre, ville=ville, user="%s"%user, prix=prix,desc = desc)
    t.put()
    return t.key().id()

def UpdateTache(valeurid,user,ajouter):
    tache = getTache(valeurid)
    if (ajouter):
        if not(user in tache.participants):
            tache.participants.append(user)
            tache.put()
    else:
        tache.participants.remove(user)
        tache.put()
    return tache