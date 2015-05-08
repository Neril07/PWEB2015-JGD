import webapp2

__author__ = 'svg'


from google.appengine.ext import db
from google.appengine.api import memcache

#@param: key represente le login de l'utilisateur voulu
#@param: update indique si il faut mettre a jour le cache
def getUtilisateur(key,update=False):

    if key == "tous":
        utilisateur=memcache.get(key)
        if not(utilisateur) or update:
            utilisateur=db.GqlQuery("SELECT * FROM Utilisateur").fetch(limit=None)
            for e in utilisateur:
                setUtilisateur(e)
            memcache.set("tous",utilisateur)
    else:
        utilisateur=memcache.get("U"+key)
        if utilisateur is None or update:
            utilisateur=db.GqlQuery("SELECT * FROM Utilisateur WHERE login = '%s'"%key).fetch(limit=1)
            if utilisateur:
                utilisateur=utilisateur[0]
                setUtilisateur(utilisateur)
    return utilisateur


#@param: utilisateur represente le model ci dessous complete
def setUtilisateur(utilisateur):
    memcache.set(utilisateur.login,utilisateur)

def lierUtilisateurResource(login, resourceId):
    utilisateur=getUtilisateur(login)
    utilisateur.resource=resourceId
    utilisateur.put()
    getUtilisateur(login,update=True)

class Utilisateur(db.Model):
    login=db.StringProperty(required=True)
    mdp=db.StringProperty(required=True)
    resource=db.StringProperty(required=False)
    droitJustification=db.BooleanProperty(default=False)
    droitAdministration=db.BooleanProperty(default=False)