# -*- coding: utf-8 -*-

def borrar_session():
    if not URL.verify(request, hmac_key=KEY): raise HTTP(403)
    session.clear()
    session.olvidado = True
    redirect(URL('default','index'))
