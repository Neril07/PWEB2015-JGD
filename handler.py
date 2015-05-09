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

        taches= Tache.getTaches(True)
        self.render('HomePageTache.html',taches = taches)

    def get(self):
        taches= Tache.getTaches(True)

        cookie=self.request.cookies.get("user_info")
        self.write(cookie)
        if cookie:
            if Authentification.validCookie(cookie) is None:
                values=cookie.split(":")
                login=Utilisateur.getUtilisateur(values[0].split('=')[1], update=True)
                #self.redirect("/" +str(memcache.get('%s'%login)))
                self.render("HomePageTache.html", taches=taches)
            else:
                self.render("HomePageTache.html", taches=taches)
        else:
            self.render("HomePageTache.html", taches=taches)



class Create(Handler):
    def render_front(self, titre="", ville="", prix="", error="",user=""):
        #user = self.request.cookies.get("user_info")
        self.render("create.html", titre=titre, ville=ville, prix=prix, error=error,user = user)


    def get(self):
        cookie=self.request.cookies.get("user_info")
        self.write(cookie)
        if cookie:
            if Authentification.validCookie(cookie) is None:
                self.render_front()
            else:
                self.render("PlzLoginIn.html")
        else:
            self.render("PlzLoginIn.html")

    def post(self):
        titre = self.request.get('titre')
        ville = self.request.get('ville')
        if (self.request.get('prix').isdigit()):
            prix = int(self.request.get('prix'))
        else:
            prix = 0
        if not prix:
            prix=0

        cookie=self.request.cookies.get("user_info")
        self.write(cookie)
        if cookie:
            if Authentification.validCookie(cookie) is None:
                values=cookie.split(":")
                user=Utilisateur.getUtilisateur(str(values[0].split('=')[1]), update=True)
                if user:
                    pseudo="pouet"
                else:
                    pseudo="defaut"
        else:
            pseudo="default"

        if titre and ville:
            desc = self.request.get('description')
            Tache.setTache(titre=titre, ville=ville, user="%s"%pseudo, prix=prix,desc = desc)
            self.redirect('/AfficherTache' )
        else :
            error = "Il faut un titre et un contenu"
            self.render_front(titre=titre, ville=ville, prix=prix, error=error)

class AfficherTache(Handler):

    def get(self):
        taches = Tache.getTaches()
        self.render("HomePageTache.html",taches = taches)

    def post(self):
        titre = self.request.get('titre')
        ville = self.request.get('ville')
        prix = int(self.request.get('prix'))
        if not prix:
            prix=0

        cookie=self.request.cookies.get("user_info")
        self.write(cookie)
        if cookie:
            if Authentification.validCookie(cookie) is None:
                values=cookie.split(":")
                user=Utilisateur.getUtilisateur(str(values[0].split('=')[1]), update=True)
                if user:
                    pseudo="pouet"
                else:
                    pseudo="defaut"
        else:
            pseudo="default"

        if titre and ville:
            tache_objet = Tache(titre=titre, ville=ville, user="%s"%pseudo, prix=prix)
            tache_objet.put()

            self.redirect('/' )
        else :
            error = "Il faut un titre et un contenu"
            self.render_front(titre=titre, ville=ville, prix=prix, error=error)

class ClearTable(Handler):
        def get(self):
            taches = Tache.getTaches()
            for tache in taches :
                Tache.suppTache(tache)
            self.redirect("/")

import Authentification