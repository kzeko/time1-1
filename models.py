from google.appengine.ext import ndb

class Opravila(ndb.Model):
    zadeva_opravila = ndb.StringProperty()
    nastanek = ndb.DateTimeProperty(auto_now_add=True)
    dokoncano = ndb.BooleanProperty(default=False)
    tedenska_prioriteta = ndb.IntegerProperty()
    dodaten_opis = ndb.TextProperty()