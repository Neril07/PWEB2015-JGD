# -*- coding: utf-8 -*-

import os
import urllib2
from xml.dom import minidom
import time

import webapp2
import jinja2


from DB_Models import Tache
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
        taches= Tache.getTaches(True)

        cookie=self.request.cookies.get("user_info")
        self.write(cookie)
        if cookie:
            if Authentification.validCookie(cookie) is None:
                values=cookie.split(":")
                login=Utilisateur.getUtilisateur(values[0].split('=')[1], update=True)
                self.redirect("/coursActuel" +str(memcache.get('%s'%login)))
            else:
                self.render("HomePageTache.html", taches=taches)
        else:
            self.render("HomePageTache.html", taches=taches)


    def post(self):
        pseudo = self.request.get('nomUtilisateur').upper()
        # on cherche la base de donnees
        if (not pseudo):
            self.render('Identification.html', erreur="Aucun utilisateur n'a ete entre")
        elif pseudo:
            #user = None
            #assert isinstance(user, model.Professeur)
            user = Utilisateur.getUtilisateurByPseudo(pseudo)
            if not user:
                self.render('Identification.html', erreur="Nous n avons pas trouve la personne demandee.")
            else:
                self.redirect("/coursActuel"+str(user.pseudo))



import Authentification