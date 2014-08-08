# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
response.KEY = KEY = 'youshallnotpass'
#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

response.menu = [
]

es_nuevo = not auth.is_logged_in() and not session.id_facultad

response.nav = auth.navbar(mode="dropdown")
if es_nuevo:
    # si no esta logueado y no tiene facultad como anonimo
    link = response.nav.element('a')
    link.components[0] = 'Iniciar'
    e = response.nav.element('.dropdown-menu')
    e.insert(0, '')
    e[0]['_class'] = 'divider'
    e.insert(0, A(I(_class='icon-question-sign'),' Anónimo',
                  _href='#modalFacultad', **{'_data-toggle': 'modal'}))
elif not auth.is_logged_in() and session.id_facultad:
    # si no esta logueado pero tiene facultad de anonimo
    link = response.nav.element('a')
    link.components[0] = 'Anónimo'
    e = response.nav.element('.dropdown-menu')
    e.insert(0, '')
    e[0]['_class'] = 'divider'
    e.insert(0, A(I(_class='icon-question-sign'),' Olvidame',
                  _href=URL('utilidades','borrar_session',hmac_key=KEY)))

if "auth" in locals(): auth.wikimenu()
