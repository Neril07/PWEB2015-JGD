# -*- coding: utf-8 -*-

import os
import urllib2
from xml.dom import minidom
import time
import re

import webapp2
import jinja2


from DB_Models import Tache
from DB_Models import Utilisateur
from google.appengine.api import memcache
import json
from google.appengine.ext import db


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
    def render_front(self, titre="", ville="", prix="", error="",user="", desc="", tags=""):
        #user = self.request.cookies.get("user_info")
        self.render("Create.html", titre=titre, ville=ville, prix=prix, erreur=error,user = user, desc=desc, tags=tags)

    def tagUnvalid(self, tag):
        if tag:
            if not re.match("^[\sa-zA-Z0-9_-]{3,20}$" , tag):
                return 'tag is unvalid!'

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
                user=Utilisateur.getUtilisateur(str(values[0].split('=')[1].split('|')[0]), update=True)
                if user:
                    pseudo=user.pseudo
                else:
                    pseudo="defaut"
        else:
            pseudo="default"

        if titre and ville:
            desc = self.request.get('description')
            tag=self.request.get('tags')
            error=""
            if tag :
                tags=tag.split(';')
                tache_id=Tache.setTache(titre=titre, ville=ville, user="%s"%pseudo, prix=prix,desc = desc)
                tache=Tache.getTache(tache_id)
                for t in tags:
                    if self.tagUnvalid(t) is None:
                        Tache.UpdateTagsTache(tache_id, t, True)
                    else:
                        error ="Il faut un tag correct (#tag1; #tag2)"
                if error=="":
                    self.redirect("/AfficherTache")

                else:
                    Tache.suppTache(tache)
                    self.render_front(titre=titre, ville=ville, prix=prix, desc=desc, error=error)
            else:
                error = "Il faut un ou des tags"
                self.render_front(titre=titre, ville=ville, prix=prix,desc=desc, error=error)
        else :
            error = "Il faut un titre et un contenu"
            self.render_front(titre=titre, ville=ville, prix=prix, error=error)

class AfficherTache(Handler):

    def get(self):
        taches = Tache.getTaches()
        self.render("HomePageTache.html",taches = taches)

class ClearTable(Handler):
        def get(self):
            taches = Tache.getTaches()
            for tache in taches :
                Tache.suppTache(tache)
            self.redirect("/")




class TachePage(Handler):
    def get(self):
        valeurid=self.request.get('valeur')
       # test = Tache.getTache(valeurid)
        key = db.Key.from_path('Tache', int(valeurid), parent=Tache.tache_key())
        test = db.get(key)
        #taches = Tache.getTaches()
        self.render("Tache.html",tache = test)

class InscrireTache(Handler):
    def get(self):
        valeurid=self.request.get('valeur')
        cookie=self.request.cookies.get("user_info")
        user = (cookie.split('|')[0]).split('=')[1]
        tache = Tache.UpdateTache(valeurid,user,True)
        self.redirect('/Tache?valeur=%s' %valeurid)

class DeInscrireTache(Handler):
    def get(self):
        valeurid=self.request.get('valeur')
        cookie=self.request.cookies.get("user_info")
        user = (cookie.split('|')[0]).split('=')[1]
        tache = Tache.UpdateTache(valeurid,user,False)
        self.redirect('/Tache?valeur=%s' %valeurid)

class SuppTache(Handler):
    def get(self):
        valeurid=self.request.get('valeur')
        cookie=self.request.cookies.get("user_info")
        user = (cookie.split('|')[0]).split('=')[1]
        tache = Tache.getTache(valeurid)
        Tache.suppTache(tache)
        self.redirect('/')

class ClearUtilisateur(Handler):
        def get(self):
            utilisateurs = Utilisateur.getUtilisateur("tous")
            for utilisateur in utilisateurs :
                Utilisateur.suppUtilisateur(utilisateur)
            self.redirect("/")


import Authentification