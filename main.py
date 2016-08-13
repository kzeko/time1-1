#!/usr/bin/env python



import os
import jinja2
import webapp2
import datetime
import time

from google.appengine.api import users
from models import Opravila

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            loggedin = True
            logout_url = users.create_logout_url("/")

            params = {"loggedin": loggedin, "logout_url": logout_url, "users":user}

            if user.email() in {"robert.dvorsek@gmail.com", "robert.dvorsek@znajdise.net"}:
                logged_rights = True
                email = user.email()
                logout_url = users.create_logout_url("/")

                params = {"loggedin": loggedin, "logged_rights":logged_rights, "logout_url":logout_url, "user": user, "email":email}

            else:
                prijavljen = False
                login_url = users.create_login_url("/")
                params = {"prijavljen": prijavljen, "login_url": login_url, "user":user}

        else:
            loggedin = False
            login_url = users.create_login_url("/")
            params = {"loggedin": loggedin, "login_url": login_url, "user":user}

        self.render_template("index.html", params=params)




class StoparcaHandler(BaseHandler):
    def get(self):

        return self.render_template("stoparca.html")

class TrenutnicasHandler(BaseHandler):
    def get(self):
        ura = time.strftime("%H: %M: %S")
        datum = datetime.datetime.now().strftime("%d. %m. %y.")
        params = {"ura": ura, "datum": datum}
        return self.render_template("trenutnicas.html", params=params)



class OpravilaHandler(BaseHandler):
    def get(self):
        params = {"sporocilo2": "Tukaj je sporocilo iz Opravilahandler"}

        return self.render_template("opravila.html", params=params)


    def post(self):
        vpis_zadeva_opravila = self.request.get("vnos_zadeva_opravila")
        vpis_dodatni_opis = self.request.get("vnos_dodaten_opis")
        vpis_tedenska_prioriteta = self.request.get("vnos_tedenska_prioriteta")
        vpis_tag = self.request.get("vnos_tag")

        opravilo = Opravila(zadeva_opravila=vpis_zadeva_opravila, dodaten_opis=vpis_dodatni_opis, tedenska_prioriteta=int(vpis_tedenska_prioriteta), tag = vpis_tag)
        opravilo.put()



        return self.redirect_to("seznam_opravil")

class PosameznoOpraviloHandler(BaseHandler):
    def get(self, opravilo_id):
        opravilo = Opravila.get_by_id(int(opravilo_id))
        params = {"opravilo": opravilo}
        return self.render_template("posamezno_opravilo.html",
                                        params=params)



###### SEZNAMI OPRAVIL ######


class SeznamOpravilHandler(BaseHandler):
    def get(self):
        seznam = Opravila.query().fetch()
        params = {"seznam": seznam}
        return self.render_template("seznam_opravil.html", params=params)

class SeznamAktivnihOpravil(BaseHandler):
    def get(self):
        seznam = Opravila.query(Opravila.izbrisano == False).fetch()
        params = {"seznam": seznam}
        return self.render_template("seznam_aktivnih_opravil.html", params=params)


###### HANDLERJI ZA MANIPULIRANJE OPRAVIL ######



class UrediOpraviloHandler(BaseHandler):
    def get(self, opravilo_id):
        opravilo = Opravila.get_by_id(int(opravilo_id))
        params = {"opravilo": opravilo}
        return self.render_template("uredi_opravilo.html", params=params)

    def post(self, opravilo_id):
        popravek_zadeva_opravila = self.request.get("uredi_zadeva_opravila")
        popravek_dodaten_opis = self.request.get("uredi_dodaten_opis")
        opravilo = Opravila.get_by_id(int(opravilo_id))
        opravilo.zadeva_opravila = popravek_zadeva_opravila
        opravilo.dodaten_opis = popravek_dodaten_opis

        opravilo.put()

        return self.redirect_to("seznam_opravil")


class IzbrisiDokoncnoHandler(BaseHandler):
    def get(self, opravilo_id):
        opravilo = Opravila.get_by_id(int(opravilo_id))
        params = {"opravilo": opravilo }

        return self.render_template("dokoncno_izbrisi_opravilo.html", params=params)

    def post(self, opravilo_id):
        opravilo = Opravila.get_by_id(int(opravilo_id))
        opravilo.key.delete()
        return self.redirect_to("seznam_opravil")

class IzbrisiVKosHandler(BaseHandler):
    def get(self, opravilo_id):
        opravilo = Opravila.get_by_id(int(opravilo_id))
        params = {"opravilo": opravilo}

        return self.render_template("izbrisi_v_kos.html", params=params)

    def post (self, opravilo_id):
        opravilo = Opravila.get_by_id(int(opravilo_id))
        opravilo.izbrisano = True
        opravilo.put()
        return self.redirect_to("seznam_opravil")


######   webapp2   ######

app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/stoparca', StoparcaHandler),
    webapp2.Route('/trenutnicas', TrenutnicasHandler),
    webapp2.Route('/opravila', OpravilaHandler),
    #webapp2.Route('/rezultat', RezultatHandler),
    webapp2.Route('/seznam_opravil', SeznamOpravilHandler, name="seznam_opravil"),
    webapp2.Route('/seznam_aktivnih_opravil', SeznamAktivnihOpravil, name="seznam_aktivnih_opravil"),
    webapp2.Route('/opravilo/<opravilo_id:\d+>', PosameznoOpraviloHandler),
    webapp2.Route('/opravilo/<opravilo_id:\d+>/uredi', UrediOpraviloHandler),
    webapp2.Route('/opravilo/<opravilo_id:\d+>/dokoncno_izbrisi', IzbrisiDokoncnoHandler),
    webapp2.Route('/opravilo/<opravilo_id:\d+>/izbrisi_v_kos', IzbrisiVKosHandler)
], debug=True)
