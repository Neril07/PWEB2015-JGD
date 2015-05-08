import time




from handler import Handler
import hashlib
import re
from DB_Models import Utilisateur


def check_secure_val(h):
    s=h.split("|")
    if hash_str(s[0])==s[1]:
        return s[0]


def hash_str(str):
    return hashlib.md5(str).hexdigest()


def make_secure_val(str):
   return "%s|%s" % (str,hash_str(str))

def validCookie(cookie):
    values=cookie.split(':')
    """if not(check_secure_val((values[0].split('='))[1]) and check_secure_val((values[1].split('='))[1]) and check_secure_val(values[2].split('=')[1].split('|')[0]) and check_secure_val(values[3].split('=')[1].split('|')[0])):
       return 'don\'t touch to the cookies!'"""
    return "pb"


def valid(username, pw, cookie):
        values=cookie.split(':')
        if check_secure_val((values[0].split('='))[1]) and check_secure_val((values[1].split('='))[1]) and check_secure_val(values[2].split('=')[1].split('|')[0]) and check_secure_val(values[3].split('=')[1].split('|')[0]):
            user=values[0].split('=')[1].split('|')[0]
            password=values[1].split('=')[1].split('|')[0]
            if pw != password or username!=user:
                return 'Invalid login'
        else:
            return 'don\'t touch to the cookies!'


class RegistrationHandler(Handler):
    def userUnvalid(self, username):
        if username:
            if not re.match("^[a-zA-Z0-9_-]{3,20}$" , username):
                return 'username is unvalid!'
        else:
            return 'enter a username!'

    def pseudoUnvalid(self, pseudo):
        if pseudo:
            if not re.match("^[a-zA-Z0-9_-]{3,20}$" , pseudo):
                return 'pseudo is unvalid!'
        else:
            return 'enter a pseudo!'

    def pwUnvalid(self, pw):
        if pw :
            if not re.match("^.{3,20}$", pw):
                return 'password invalid!'
        else:
            return 'enter a password!'

    def pwbisUnvalid(self, pw, pwbis):
        if pw:
            if pwbis and not self.pwUnvalid(pwbis) and pwbis!=pw:
                return 'password didn\'t match!'
            elif not self.pwUnvalid(pwbis) and pwbis==pw:
                return ''
            else:
                return 're-enter your password!'

    def get(self):
        self.render("SignIn.html")

    def post(self):
        user=self.request.get('username')
        pw=self.request.get('password')
        pwbis=self.request.get('verify')
        pseudo=self.request.get('pseudo')
        if (self.userUnvalid(user) or self.pwUnvalid(pw) or self.pwbisUnvalid(pw,pwbis) or self.pseudoUnvalid(pseudo)):
            self.render("SignIn.html",user=user, pw=pw, usernameError= self.userUnvalid(user), passwordError= self.pwUnvalid(pw), verify= self.pwbisUnvalid(pw, pwbis), pseudoError=self.pseudoUnvalid(pseudo))
        else:
            utilisateur=Utilisateur.getUtilisateurByPseudo(pseudo)
            if not(utilisateur):
                pw=str(make_secure_val(pw))
                u=Utilisateur.Utilisateur(login=user, mdp=pw, pseudo=pseudo)
                u.put()
                time.sleep(1)
                self.redirect('/login')
            else:
                self.render("SignIn.html",user=user, userError="" , passwordError="", verify="", pseudoError="ce pseudo est deja utilise")

class LoginHandler(Handler):
    def get(self):
        self.render("Login.html")

    def post(self):
        login=self.request.get('username')
        pw=str(make_secure_val(self.request.get('password')))
        utilisateur=Utilisateur.getUtilisateur(login)
        if not(utilisateur) or utilisateur.mdp!=pw:
            self.render("Login.html",error="Mauvaise combinaison login/password",username=login)
        else:
            if self.request.get('Remember')=="on":
                expire="; expires=31-Dec-2020 23:59:59 GMT"
            else:
                expire=""
            self.response.headers.add_header('Set-Cookie', 'user_info=username=%s:pw=%s:pseudo=%s ; Path=/ %s' % (str(make_secure_val(login)), pw, str(utilisateur.pseudo), expire))
            self.redirect('/')

class LogOutHandler(Handler):
    def get(self):
        self.response. headers.add_header('Set-Cookie', 'user_info=; Path=/')
        self.redirect('/')