# -*- coding: utf-8 -*-

import os
import urllib2
from xml.dom import minidom
import time

import webapp2
import jinja2

from DB_Models import Utilisateur
from google.appengine.api import memcache
import json



template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        cookie=self.request.cookies.get('user_info')
        self.write(self.render_str(template, cookie=cookie, **kw))




    def getNomsGroups(self, update=False):
         groupes = memcache.get('groupes')
         if (not groupes) or update:
            groupes = self.getNomsGroupsSansLeCache()
            memcache.set('groupes', groupes)
         return groupes

    def getNomsCoursSansLeCache(self):
       sessionId = self.connexion()
       contentActif = urllib2.urlopen('https://adeweb.univ-lorraine.fr/jsp/webapi?sessionId=%s&function=getResources&detail=13' % sessionId).read()
       contentXMLActif = minidom.parseString(contentActif)

       resourcesList = contentXMLActif.getElementsByTagName('resource')
       listeCours = []

       for resource in resourcesList:
           if (resource.getAttribute('category')=='category6'):
               cours = {}
               cours['name']= resource.getAttribute('name')
               cours['id'] = resource.getAttribute('id')
               listeCours.append(cours)
       return listeCours

    def getNomsCours(self, update=False):
         courss = memcache.get('cours')
         if (not courss) or update:
            courss = self.getNomsCoursSansLeCache()
            memcache.set('cours', courss)
         return courss

class MainHandler(Handler):
    def render_font(self):
        self.render('HomePage.html')

    def get(self):
        cookie=self.request.cookies.get("user_info")
        self.write(cookie)
        if cookie:
            if Authentification.validCookie(cookie) is None:
                values=cookie.split(":")
                utilisateur=Utilisateur.getUtilisateur(values[0])
                if utilisateur.resource:
                    user = Professeur.getProfesseurByName(utilisateur.resource)
                    if len(user)==0:
                        user = Etudiant.getEtudiantByName(utilisateur.resource)
                        self.redirect("/coursActuel"+str(user[0].id))
                    else:
                        self.redirect("/coursActuel"+str(user[0].id))
            else:
                self.render("Identification.html")
        else:
            self.render("Identification.html")


    def post(self):
        nomUtilisateur = self.request.get('nomUtilisateur').upper()
        # on cherche la base de donnees
        if (not nomUtilisateur):
            self.render('Identification.html', erreur="Aucun utilisateur n'a ete entre")
        elif nomUtilisateur:
            #user = None
            #assert isinstance(user, model.Professeur)
            user = Professeur.getProfesseurByName(nomUtilisateur)
            if len(user)==0:
                user = Etudiant.getEtudiantByName(nomUtilisateur)
                if len(user)==0:
                    self.render('Identification.html', erreur="Nous n avons pas trouve la personne demandee.")
                else:
                    self.redirect("/coursActuel"+str(user[0].id))
            else:
                self.redirect("/coursActuel"+str(user[0].id))


    def essaiAffichageAbsences(self):
        absences = [{'date': '01/01/2014', 'horaires': '8h-10h', 'cours': 'Manger', 'absents': ['Nom1','Nom2']},
                    {'date': '01/01/2014', 'horaires': '10h-12h', 'cours': 'Dormir', 'absents': ['Nom1']},
                    {'date': '01/01/2014', 'horaires': '10h-12h', 'cours': 'Chanter', 'absents': ['Nom2']},
                    {'date': '01/01/2014', 'horaires': '16h-18h', 'cours': 'Valser', 'absents': ['Nom1']}]

        self.render("EssaiAffichageAbsences.html", absences=absences)

class CoursActuel(Handler):
    def get(self,userId):
        self.render("Identification.html")

    def post(self,userId):
        nomUtilisateur = self.request.get('nomUtilisateur').upper()
        # on cherche la base de donnees
        if nomUtilisateur:
            #user = None
            #assert isinstance(user, model.Professeur)
            user = Professeur.getProfesseurByName(nomUtilisateur)
            if len(user)!=1:
                user = Etudiant.getEtudiantByName(nomUtilisateur)
                if len(user)!=1:
                    self.render('Identification.html', erreur="Nous n avons pas trouve la personne demandee."+nomUtilisateur)
                # autocomplétion ?
                else:
                    self.quelCoursAiJe(userId=userId)
            else:
                self.quelCoursAiJe(userId=userId)


    def quelCoursAiJe(self, userId="355"):

        # on recupere sessionId & on se rattache au projet TN
        """sessionId = self.connexion()

        # on recupere la date actuelle
        #date=time.strftime('%m/%d/%Y',time.localtime())
        date = ('03/03/2014')
        # actuellement, on a l'id de la personne
        #userId = 355

        # on charge la page des events a la date convenue et ou la personne est mentionnee
        content=urllib2.urlopen('https://adeweb.univ-lorraine.fr/jsp/webapi?sessionId=%s&function=getEvents&detail=8&date=%s&resources=%s' % (sessionId,date,userId)).read()

        # on y cherche un event via l'heure de debut et l'heure de fin
        contentXML = minidom.parseString(content)
        eventsList= contentXML.getElementsByTagName("event")

        # heure actuelle
        heure = time.strftime('%H:%M',time.localtime())
        h,m = heure.split(':')[0],heure.split(':')[1]
        h = int(h)+2
        coursActuellement = False
        for event in eventsList:
            debut = str(event.getAttribute('startHour'))
            fin =  str(event.getAttribute('endHour'))

            hdebut, mdebut = int(debut.split(':')[0]),int(debut.split(':')[1])
            hfin, mfin = int(fin.split(':')[0]),int(fin.split(':')[1])

            if ((h==hdebut and m>=mdebut) or (h>hdebut and h<hfin) or (h==hfin and m<=mfin)):
                coursActuellement = True
                idCours = event.getAttribute('id')

                # tentage d'optimisation (limiter les requetes)
                resources = event.getElementsByTagName('resource')
                classroom=''
                prof=''
                eleves=''
                for r in resources:
                    if (r.getAttribute('category')=='classroom'):
                        classroom=r.getAttribute('name')
                    elif (r.getAttribute('category')=='instructor'):
                        prof=r.getAttribute('name')
                    elif (r.getAttribute('category')=='trainee'):
                        eleves = r.getAttribute('name')

                if eleves :
                    listeEleves
                    = self.quiEstDansCeGroupe(eleves)
                #self.write('Tu as %s de %s a %s en %s avec le/la prof %s<br>' % (event.getAttribute('name'),str(debut),str(fin),classroom, prof))
                #self.write(' et avec :<br>%s' %self.quiEstDansCeGroupe(eleves))

                self.render("CurrentCoursePage.html", courseBoolean=True, listeEleves = listeEleves, eleves=eleves, cours = event.getAttribute('name'), heureDebut = str(debut), heureFin = str(fin), classroom=classroom, prof=prof)

        if (coursActuellement == False):
            #self.write('Soline, tu as n\'as pas cours la.<br>')
            self.render("CurrentCoursePage.html", courseBoolean = False)
        """

        heure = time.strftime('%H',time.localtime())
        heure+=':45'
        courses=self.getCours(heure)
        resource=Professeur.getProfesseur(userId)
        trouve = False
        if resource:
            i=0
            while i in range(len(courses)):
                cours=courses[i]
                if cours["prof"]==resource.nomPrenom:
                    groupes=cours["groupes"].split(";")
                    listeEleves=[]
                    for j in range(len(groupes)-1):
                        listeEleves+=Etudiant.getGroupe(groupes[j])
                    self.render("CurrentCoursePage.html",cours=cours,prof=cours["prof"],listeEleves=listeEleves)
                    break
                i+=1
        else:
            resource=Etudiant.getEtudiant(userId)
            for cours in courses:
                #self.write(cours)
                groupesCours=cours["groupes"].split(";")
                i=0
                while i<len(groupesCours)-1 and groupesCours[i] not in resource.groupes:
                    i+=1
                if i!=len(groupesCours)-1:
                    trouve = True
                    listeEleves=[]
                    for j in range(len(groupesCours)-1):
                        listeEleves+=Etudiant.getGroupe(groupesCours[j])
                    self.render("CurrentCoursePage.html",cours=cours,listeEleves=listeEleves)
        if (not trouve):
            self.render("CurrentCoursePage.html",cours="",listeEleves=[])

    def quiEstDansCeGroupe(self, nomGroupe):
        nomGroupePath = '.'+nomGroupe+'.'
        ret=''
        #connexion & rattachement a TN
        sessionId = self.connexion()

        # on va recuperer la liste des eleves de IL
        contentActif = urllib2.urlopen('https://adeweb.univ-lorraine.fr/jsp/webapi?sessionId=%s&function=getResources&detail=13' % sessionId).read()
        contentXMLActif = minidom.parseString(contentActif)

        resourcesList = contentXMLActif.getElementsByTagName('resource')
        dicoGroup = {}
        listeEleves = [];

        for resource in resourcesList:
            #if (resource.getAttribute('category')=='trainee'):
                #self.write('Groupe : %s<br>' % resource.getAttribute('name'))
            if ((nomGroupePath in resource.getAttribute('path')) or (nomGroupe == resource.getAttribute('name'))):
                if (resource.getAttribute('category')=='trainee'):
                    elements = resource.getElementsByTagName('allMembers')
                    for element in elements:
                        elem=element.getElementsByTagName('member')
                        for el in elem:
                            #self.write(el.getAttribute("name")+'<br>')
                            #ret = ret+el.getAttribute("name")+'<br>'
                            listeEleves.append(el.getAttribute("name"));
        return listeEleves

class EdtDuJour(Handler):
    def get(self):
        self.affichageEdt()

    def affichageEdt(self):
        courses = [{'title':'cours1', 'horaires': '8h - 10h', 'classroom':'E1kekchose', 'group': 'IL', 'absents': ['moi11']},
                        {'title':'cours2', 'horaires': '10h - 12h', 'classroom':'E1kekchose', 'group': 'IL', 'absents': ['moi21', 'moi22', 'moi12','moi21', 'moi22', 'moi12','moi21', 'moi22', 'moi12','moi21', 'moi22', 'moi12','moi21', 'moi22', 'moi12']},
                        {'title':'cours3', 'horaires': '14h - 16h', 'classroom':'E1kekchose', 'group': 'IL', 'absents': []},
                        {'title':'cours4', 'horaires': '16h - 18h', 'classroom':'E1kekchose', 'group': 'IL', 'absents': ['moi41', 'moi42']}];

        self.render("EssaiEdTJour.html", courses=courses)

class CompoGroupes(Handler):
    def get(self):
        groupes = self.getNomsGroups()
        groupes = sorted(groupes, key=lambda groupe: groupe['name'])
        self.render("AffichageCompoGroupes.html", groupes = groupes, erreur = "", membres = [])

    def post(self):
        groupe = self.request.get("groupe")
        etudiants = Etudiant.getGroupe(groupe)

        groupes = self.getNomsGroups()
        groupes = sorted(groupes, key=lambda groupe: groupe['name'])

        self.render("AffichageCompoGroupes.html", groupes = groupes, erreur = "", membres = etudiants, nb = len(etudiants), groupe=groupe)
        #self.render("AffichageCompoGroupes.html", etudiants = etudiants, nb = len(etudiants), groupe = memcache.get(groupe))
        #TODO : to be continued...


class ListeAbsences(Handler):
    def get(self):
        #dico = json.dumps({"GRO 2A": [{'date':'03/03/2014', 'heureDebut':'8', 'heureFin':'10'}, {'date':'04/03/2014', 'heureDebut':'10', 'heureFin':'12'}]})
        # on recupere les groupes et on les trie par ordre alphabetique des noms
        groupes = self.getNomsGroups()
        groupes = sorted(groupes, key=lambda groupe: groupe['name'])

        # on recupere les cours et on les trie par ordre alphabetique des noms
        courss = self.getNomsCours()
        courss = sorted(courss, key = lambda cours: cours['name'])

        self.render("ConsulterAbsencesForm.html", groupes = groupes, courss = courss, erreur = "")

        # demander si on veut la liste des absences pour :
            # un etudiant -> recherche de nom
            # un groupe -> liste deroulante par ordre alphabetique
            # un cours -> liste deroulante

    def post(self):
        nomCherche = self.request.get("etudiant")
        groupeCherche = self.request.get("groupe")
        coursCherche = self.request.get("cours")
        idEtudiant = self.request.get("idEtudiant")
        etudiantTrouve = None

        if (idEtudiant):
            etudiantTrouve = Etudiant.getEtudiant(idEtudiant)
            #self.render("AffichageAbsencesChoixPersonnes.html", erreur=etudiant.nomPrenom)

        else:
            if ((not nomCherche) and (not groupeCherche) and (not coursCherche)):
                    self.render("ConsulterAbsencesForm.html", groupes = "", courss = "", erreur = "Merci d'entrer un nom d'etudiant.")
            elif nomCherche:
                # On recupere la liste des etudiants et on cherche parmi eux en fonction du nom
                etudiants = Etudiant.getEtudiant("tous")
                etudiantsTrouves = []
                for etudiant in etudiants:
                    if nomCherche.lower() in (etudiant.nomPrenom).lower():
                        etudiantsTrouves.append(etudiant)

                if (len(etudiantsTrouves)>0):
                    #si plus d'une proposition
                    self.render("AffichageAbsencesChoixPersonnes.html", etudiantsTrouves=etudiantsTrouves, coursCherche = coursCherche)
                    #self.render("AffichageAbsencesChoixPersonnes.html", etudiantsTrouves=idEtudiant)

                elif (len(etudiantsTrouves)==0):
                    # si aucun etudiant ne correspond
                    # on recupere les groupes et on les trie par ordre alphabetique des noms
                    groupes = self.getNomsGroups()
                    groupes = sorted(groupes, key=lambda groupe: groupe['name'])
                    # on recupere les cours et on les trie par ordre alphabetique des noms
                    courss = self.getNomsCours()
                    courss = sorted(courss, key = lambda cours: cours['name'])
                    self.render("ConsulterAbsencesForm.html", groupes = groupes, courss = courss, erreur = "Nous n'avons pas trouve l'etudiant concerne.")

                #else:
                    # si seul un etudiant correspond
                #    etudiantTrouve = etudiantsTrouves[0]

        # si la recherche porte sur un etudiant et un cours
        if (etudiantTrouve and coursCherche):
            absences = self.recupAbsencesEtudiantCours(etudiantTrouve, coursCherche)
            # TODO : trier chronologiquement
            self.render("AffichageAbsencesEtudiantCours.html", absences = absences, etudiant = etudiantTrouve.nomPrenom, cours = coursCherche, nbAbs = len(absences))

        # si la recherche porte sur un groupe et un cours
        elif ((not nomCherche) and groupeCherche and coursCherche) :
            absences = self.recupAbsencesGroupeCours(groupeCherche, coursCherche)
            nbAbs = absences[1]
            absences = absences[0]
            # TODO : trier chronologiquement
            self.render("AffichageAbsencesGroupeCours.html", absences = absences, groupe =groupeCherche, cours = coursCherche, nbAbs = nbAbs)

        # si la recherche porte sur un etudiant seulement
        elif (etudiantTrouve and (not coursCherche)):
            absences = self.recupAbsencesEtudiant(etudiantTrouve)
            # TODO : trier chronologiquement
            self.render("AffichageAbsencesEtudiant.html", absences = absences, etudiant = etudiantTrouve, nbAbs = len(absences))

        # si la recherche porte sur un cours seulement
        elif (coursCherche and (not nomCherche) and (not groupeCherche)):
            absences = self.recupAbsencesCours(coursCherche)
            nbAbs = absences[1]
            absences = absences[0]
            self.render("AffichageAbsencesCours.html", absences = absences, cours = coursCherche, nbAbs = nbAbs)
            # TODO : on trie chronologiquement

        # si la recherche porte sur un groupe seulement
        elif (groupeCherche and (not nomCherche) and (not coursCherche)):
            absences = self.recupAbsencesGroupe(groupeCherche)
            nbAbs = absences[1]
            absences = absences[0]
            self.render("AffichageAbsencesGroupe.html", absences = absences, groupe = groupeCherche, nbAbs = nbAbs)

        # si le temps : faire la meme chose en pouvant choisir entre deux dates

    def recupAbsencesGroupe(self, groupe):
        absences = {}
        i=0
        #self.write('<br><br><br><br><br><br><br><br><br>')
        # on recupere tous les etudiants du groupe
        etudiants = Etudiant.getGroupe(groupe)
        # on recupere toutes leurs absences au cours
        for etu in etudiants:
            #self.write(etu.nomPrenom)
            abs = etu.absences
            abs = json.loads(abs)

            #self.write('<br>')
            #self.write(len(abs))
            for cours in abs:
                #self.write(etu.nomPrenom)
                abs = abs[cours]  # on a la liste des absences de l'eleve au cours


                for ab in abs:
                    if not (ab["date"] in absences):
                        absences[ab["date"]] = {}
                    if not (ab['heureDebut'] in absences[ab['date']]):
                        absences[ab['date']][ab['heureDebut']] = {}
                    if not (ab["heureFin"] in absences[ab['date']][ab['heureDebut']]):
                        absences[ab['date']][ab['heureDebut']][ab["heureFin"]] = {}
                    if not (cours in absences[ab['date']][ab['heureDebut']][ab["heureFin"]]):
                        absences[ab['date']][ab['heureDebut']][ab["heureFin"]][cours] = []

                    absences[ab["date"]][ab["heureDebut"]][ab["heureFin"]][cours].append(etu.nomPrenom)
                    i=i+1
        return [absences,i]

    def recupAbsencesEtudiant(self, etudiant):
        absences = {}
        absences = etudiant.absences
        absences = json.loads(absences)
        #st = '{"GRO 2A": [{"date": "03/03/2014", "heureFin": "10", "heureDebut": "8"}, {"date": "04/03/2014", "heureFin": "12", "heureDebut": "10"}]}'
        #abs = json.loads(st)
        absReturn = []
        for cours in absences:
            abs = {}
            abs = absences[cours]
            for a in abs:
                a['cours'] = cours
                absReturn.append(a)
        return absReturn

    def recupAbsencesEtudiantCours(self, etudiant, cours):
        absences = {}
        absences = etudiant.absences
        absences = json.loads(absences)
        #self.write('<br><br><br><br><br><br><br>')
        if cours in absences:
            absences = absences[cours]
            #self.write(cours)
        else:
            absences = []
            #self.write('rien')

        return absences

    def recupAbsencesGroupeCours(self, groupe, cours):
        absences = {}
        i=0;
        # on recupere tous les etudiants du groupe
        etudiants = Etudiant.getGroupe(groupe)
        # on recupere toutes leurs absences au cours
        for etu in etudiants:
            abs = etu.absences
            abs = json.loads(abs)
            if cours in abs:
                abs = abs[cours]  # on a la liste des absences de l'eleve au cours
            else:
                abs = []

            for ab in abs:
                if not (ab["date"] in absences):
                    absences[ab["date"]] = {}
                if not (ab['heureDebut'] in absences[ab['date']]):
                    absences[ab['date']][ab['heureDebut']] = {}
                if not (ab["heureFin"] in absences[ab['date']][ab['heureDebut']]):
                    absences[ab['date']][ab['heureDebut']][ab["heureFin"]] = []

                i=i+1
                absences[ab["date"]][ab["heureDebut"]][ab["heureFin"]].append(etu.nomPrenom)
        return [absences, i]

    def recupAbsencesCours(self, cours):
        absences = {}
        i=0
        # on recupere tous les etudiants du groupe
        etudiants = Etudiant.getEtudiant("tous")
        # on recupere toutes leurs absences au cours
        for etu in etudiants:
            abs = etu.absences
            abs = json.loads(abs)

            if cours in abs:
                abs = abs[cours]  # on a la liste des absences de l'eleve au cours
            else:
                abs = []

            for ab in abs:
                if not (ab["date"] in absences):
                    absences[ab["date"]] = {}
                if not (ab['heureDebut'] in absences[ab['date']]):
                    absences[ab['date']][ab['heureDebut']] = {}
                if not (ab["heureFin"] in absences[ab['date']][ab['heureDebut']]):
                    absences[ab['date']][ab['heureDebut']][ab["heureFin"]] = []

                absences[ab["date"]][ab["heureDebut"]][ab["heureFin"]].append(etu.nomPrenom)
                i=i+1
        return [absences,i]

class AbsHandler(Handler):
    def post(self,nombreetudiant):
        Nomcours = self.request.get("nomCours")
        DateCours=time.strftime('%m/%d/%Y',time.localtime())
        debutCours = self.request.get("debutCours")
        FinCours = self.request.get("FinCours")
        ModuleCours = self.request.get("module")
        for i in range(int(nombreetudiant)):
            etuId= self.request.get("eleve"+str(i))
            #self.write("coucou")
            if(etuId):
                etudiant = Etudiant.getEtudiant(etuId)
                etudiant = Etudiant.Etudiant.get_by_id(etudiant.key().id())
                #etudiant = etudiant.get_by_id(etudiant.ids)
                #etudiant.key()

                abs = etudiant.absences
                absences=json.loads(abs)
                if not (ModuleCours in absences):
                    absences[ModuleCours]=[]
                absences[ModuleCours].append({"date": DateCours,"heureDebut": debutCours,"heureFin" : FinCours})
                absences = json.dumps(absences)

                Etudiant.supp(etudiant)
                etudiant.absences=absences

                Etudiant.setEtudiant(etudiant)
                etudiant.put()


        self.redirect("/")

import Authentification