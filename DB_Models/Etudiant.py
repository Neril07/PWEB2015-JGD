from google.appengine.ext import db
from google.appengine.api import memcache
import json


#@param: key represente l'id de l'etudiant voulu ou "tous" si jamais on veut tous les eleves
#@param: update indique si il faut mettre a jour le cache
def getEtudiant(key,update=False):
    etudiant=memcache.get("E"+key)
    if etudiant is None or update:
        if key=="tous":
            etudiant=db.GqlQuery("SELECT * FROM Etudiant ORDER BY nomPrenom ASC").fetch(limit=None)
            memcache.set("E"+key,etudiant)
        else:
            etudiant=db.GqlQuery("SELECT * FROM Etudiant WHERE id= '%s'"%key).fetch(limit=1)
            if etudiant:
                etudiant=etudiant[0]
                setEtudiant(etudiant)
    return etudiant

#@param: etudiant represente le model ci dessous complete
def setEtudiant(etudiant):
    memcache.set("E"+etudiant.id,etudiant)

#@param: key represente le nom du groupe(penser que IL=2A IL+3A IL)
#@param: update indique si il faut mettre a jour le cache
def getGroupe(key,update=False):
    groupe=memcache.get(key)
    if groupe is None or update:
        groupe=[]
        etudiants=getEtudiant("tous")
        for i in range(len(etudiants)):
            if key in etudiants[i].groupes:
                groupe.append(etudiants[i])
        memcache.set(key,groupe)
    return groupe

# pour recuperer la liste de tous les etudiants
def getEtudiants(update=False):
    etudiants = memcache.get('etudiants')
    if (not etudiants) or update:
        etudiants = db.GqlQuery("SELECT * FROM Etudiant ORDER BY nomPrenom")
        memcache.set('etudiants', etudiants)
    return etudiants


def getEtudiantByName(nom):
    etudiant = db.GqlQuery("SELECT * FROM Etudiant WHERE nomPrenom = '%s'" % nom).fetch(limit=None)
    return etudiant

def supp(etudiant):
    etudiant.delete()

class Etudiant(db.Model):
    nomPrenom = db.StringProperty(required=True)
    id=db.StringProperty(required=True)
    #string de la forme: 'Promo Groupe\s?SousGroupe;Promo Groupe\s?SousGroupe'git
    groupes=db.StringProperty(required=True)
    #dictionnaire sous forme JSON
    absences=db.StringProperty(required=False, default=json.dumps({}))
