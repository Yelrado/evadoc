# -*- coding: utf-8 -*-
#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.domain = 'http://127.0.0.1:8000/evadoc/default'
response.logo = B(request.application.replace('_',' ').title())
response.title = request.application.replace('_',' ').title()
response.universidad = 'Benemérita Universidad Autónoma de Puebla - BUAP'
response.subtitle = ''

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Anonymous'
response.meta.description = 'Revisa a los profesores de la ' + response.universidad \
        + ' recomiendalos y lee reseñas sobre ellos'
response.meta.keywords = 'califica, profesor, revisa, recomienda, profe'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = None
response.google_webmaster = None
