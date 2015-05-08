
__author__ = 'svg'

from handler import Handler
import urllib2
from xml.dom import minidom
from DB_Models import Professeur
from DB_Models import Etudiant
from DB_Models import Utilisateur
from google.appengine.ext import db
import json

class AdmistrationHandler(Handler):
    def get(self):
        #db.GqlQuery("DELETE * FROM Professeur")
        #db.GqlQuery("DELETE * FROM Etudiant")
        cookie=self.request.cookies.get("user_info")
        if cookie:
            username,pw,droitJustif,droitAdmin=cookie.split(":")
            if droitAdmin=="True":
                utilisateurs=Utilisateur.getUtilisateur("tous")
                resources=Etudiant.getEtudiant("tous")
                resources.append(Professeur.getProfesseur("tous"))
                self.render("Administration.html", error="", youpi="",youpi2="",error2="", utilisateurs=utilisateurs,resources=resources)
            else:
                self.render("NotEnoughtRights.html")
        else:
            self.render("PlzLoginIn.html")
    def post(self):
        numProjet=self.request.get("numProjet")
        compte=self.request.get("compte")
        resourceId=self.request.get("resource")
        compteJustif=self.request.get("compteJustif")
        youpi=""
        youpi2=""
        youpi3=""
        if numProjet:
            self.recupEtudiant(numProjet)
            self.recupProf(numProjet)
            youpi="La base a ete mise a jour"
        if compte and resourceId:
            Utilisateur.lierUtilisateurResource(login=compte,resourceId=resourceId)
            youpi2="Ces Deux comptes ont bien ete lie"
        if compteJustif:
            utilisateur=Utilisateur.Utilisateur.get_by_id(Utilisateur.getUtilisateur(compteJustif).key().id())
            utilisateur.droitJustification=True
            utilisateur.put()
            Utilisateur.setUtilisateur(utilisateur)
            youpi3="Le compte specifie a desormais les droits de justification des absences"

        self.render("Administration.html", error="", youpi=youpi,error2="",youpi2=youpi2,youpi3=youpi3,error3="")

    def recupEtudiant(self, numeroProjet):
        sessionID=self.connexion(numeroProjet=numeroProjet)
        content=urllib2.urlopen('https://adeweb.univ-lorraine.fr/jsp/webapi?sessionId=%s&function=getResources&detail=13'% sessionID).read()
        #contentXML=minidom.parse('groups.txt')
        contentXML = minidom.parseString(content)
        #self.write(contentXML)
        resourceList = contentXML.getElementsByTagName('resource')

        #self.write("ya quoi comme ressource?<br>")
        #self.write(resourceList)
        #self.write("apperement que ca!<br>")
        for i in range(resourceList.length):
            if resourceList[i].getAttribute('category')=='category5' and resourceList[i].getAttribute('isGroup') == "false":
                nomPrenom=resourceList[i].getAttribute('name')
                id=resourceList[i].getAttribute('id')
                group=resourceList[i].getElementsByTagName('memberships')
                group=group[0].childNodes
                groupe=''
                for y in range(group.length):
                    if group[y].nodeName == "membership":
                        groupe+=group[y].getAttribute('name')+';'
                etudiant=Etudiant.Etudiant(nomPrenom=nomPrenom, id=id,groupes=groupe)
                #self.write("nouh")
                Etudiant.setEtudiant(etudiant)
                #time.sleep(1)
                etudiant.put()
                #time.sleep(1)


    def recupProf(self, numeroProjet):
        sessionID=self.connexion(numeroProjet=numeroProjet)
        content=urllib2.urlopen('https://adeweb.univ-lorraine.fr/jsp/webapi?sessionId=%s&function=getResources&detail=13'% sessionID).read()
        #contentXML=minidom.parse('groups.txt')
        contentXML = minidom.parseString(content)

        resourceList = contentXML.getElementsByTagName('resource')

        for resource in resourceList:
            if resource.getAttribute('category')=='instructor':
                nomPrenom=resource.getAttribute('name')
                id=resource.getAttribute('id')
                i=Professeur.Professeur(nomPrenom=nomPrenom, id=id)
                i.put()
                Professeur.setProfesseur(i)

class JustificationHandler(Handler):
    def get(self):
        cookie=self.request.cookies.get('user_info')
        if cookie :
            username,pw,droit=cookie.split(':')
            if droit=='justification=True':
                etudiants=Etudiant.getEtudiant("tous")
                self.render("justification.html",etudiants=etudiants)
            else:
                self.render('NotEnoughtRights.html')
        else:
            self.render('PlzLoginIn.html')


    def post(self):
        eleve=self.request.get("eleve")
        if "|" in eleve:
            cours,date,heureDebut=eleve.split("|")
            eleve=self.request.get("id")
            etudiant=Etudiant.getEtudiant(eleve)
            absencesDuCours=json.loads(etudiant.absences)[cours]
            for i in range(absencesDuCours):
                if absencesDuCours[i]["date"]==date and absencesDuCours[i]["heureDebut"]==heureDebut:
                    del absencesDuCours[i]
            self.redirect("/justif")
        else:
            etudiants=Etudiant.getEtudiant("tous")
            etudiant=Etudiant.getEtudiant(eleve)
            self.render("justification.html", absences=etudiant.absences, etudiants=etudiants,etudiant=eleve)
