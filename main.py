#!/usr/bin/env python



import os
import jinja2
import webapp2
import datetime
import time
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
        return self.render_template("index.html")

class StoparcaHandler(BaseHandler):
    def get(self):

        params = {"sporocilo": "Tukaj je sporocilo iz Stoparcahandler"}

        return self.render_template("stoparca.html", params=params)

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

        zadeva_opravila = Opravila(zadeva_opravila=vpis_zadeva_opravila)
        zadeva_opravila.put()
        dodaten_opis_opravila = Opravila(dodaten_opis=vpis_dodatni_opis)
        dodaten_opis_opravila.put()


        return self.redirect_to("seznam_opravil")


class SeznamOpravilHandler(BaseHandler):
    def get(self):
        seznam = Opravila.query().fetch()
        params = {"seznam": seznam}
        return self.render_template("seznam_opravil.html", params=params)



class PosameznoOpraviloHandler(BaseHandler):
    def get(self, opravilo_id):
        opravilo = Opravila.get_by_id(int(opravilo_id))
        params = {"opravilo": opravilo}
        return self.render_template("posamezno_opravilo.html",
    params=params)

app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/stoparca', StoparcaHandler),
    webapp2.Route('/trenutnicas', TrenutnicasHandler),
    webapp2.Route('/opravila', OpravilaHandler),
    #webapp2.Route('/rezultat', RezultatHandler),
    webapp2.Route('/seznam_opravil', SeznamOpravilHandler, name="seznam_opravil"),
    webapp2.Route('/opravilo/<opravilo_id:\d+>', PosameznoOpraviloHandler),
], debug=True)
