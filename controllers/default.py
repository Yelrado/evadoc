# formulario buscador
form_buscar = SQLFORM.factory(
  Field('buscar',
    requires=[IS_NOT_EMPTY(), IS_LENGTH(minsize=4,
      error_message='Prueba con un nombre más largo')]),
  _class='navbar-search pull-right',
  formstyle='divs')
input = form_buscar.element('.string')
input['_class'] = 'string search-query typeahead'
input['_id'] = 'buscador'
input['_autocomplete'] = 'off'
input['_placeholder'] = 'Buscar'
response.form_buscar = form_buscar
if response.form_buscar.validate(formname='buscador'):
    redirect(URL('default', 'buscar',
        vars=dict(q=str(form_buscar.vars.buscar))))

# formulario seleccionar facultad
if es_nuevo:
    form_facultad = SQLFORM.factory(Field('facultad',
      requires=IS_IN_DB(db, 'dependencia.id', '%(nombre)s',
                        zero='Elige tu facultad',
                        error_message='Necesitas elegir una facultad')),
                                 formstyle='divs')
    form_facultad.vars.facultad = session.id_facultad
    response.form_facultad = form_facultad
    if form_facultad.validate(formname='form_facultad'):
        session.id_facultad = form_facultad.vars.facultad
        response.flash = 'Redirigiendo a la pasarela'
        redirect(URL('default', 'pasarela'))
    elif form_facultad.errors:
        response.flash = 'Hubo un error al elegir tu facultad'

def __keywords(*claves):
    palabra = []
    for clave in claves:
        x = clave.split()
        if len(x) > 1:
            palabra += x
    todas = list(claves) + palabra
    return ','.join(todas)

def __captcha_field(request=request):
    from gluon.tools import Recaptcha
    w = lambda x,y: Recaptcha(request,
                              '6LfBhe0SAAAAALq3aWefsyTKP_Fs16t7nkd4EeWZ',
                              '6LfBhe0SAAAAADpOELwzYHmp1rGiBamQ09AL5xTe')
 
    return Field('captcha', 'string', label='Escribe las dos palabras', widget=w, default='ok')

def index():
    """
    En la página principal se muestran a profesores aleatorios
    también se muestra el total de profesores que están en la
    base de datos.
    Contiene un formulario con las facultades registradas,
    el formulario se encarga de almacenar
    la facultad en caso de tratarse de un usuario anonimo,
    después redirige a la pasarela
    """
    response.generic_patterns = ['*.html']
    numero = 24
    profesores = db().select(db.profesor.ALL,
                orderby='<random>',limitby=(0, numero),
                cache=(cache.ram, 3600),
                cacheable=True)
    resenias = db(db.evaluacion).count(cache=(cache.ram, 3600))
    total = db(db.profesor).count(cache=(cache.ram, 3600))
    if session.nuevo:
        # mensaje para elegir facultad
        del session.nuevo
        response.flash = 'Registrate o inicia como anónimo'
    if session.olvidado:
        del session.olvidado
        response.flash = '¡Ah! no te había visto, ¿eres nuevo por aquí?'

    response.meta.description = 'Revisa a los profesores de la ' + response.universidad \
        + ' recomiendalos y lee reseñas sobre ellos'
    response.meta.keywords = __keywords(response.universidad,'profesores',
        'reseña','recomienda','evalua a tu profesor')
    return dict(profesores=profesores,total=total,resenias=resenias)


def __validar_usuario():
    # obtener el id de la facultad
    if auth.user_id:
        # primero para un usuario registrado
        return db.auth_user(auth.user_id).facultad
    elif session.id_facultad:
        # si falla obtener id por session
        return session.id_facultad
    else:
        # llevar a la página de inicio
        session.nuevo = True
        redirect(URL('default', 'index'))


def pasarela():
    """
    Se muestran profesores ordenados por orden alfabetico seleccionados
    de acuerdo a la facultad de un usuario registrado o a través
    del formulario para un usuario anonimo.
    El formulario de busqueda (autocompletado) y dirige a la página
    de busqueda.
    Se extraen dos profesores, el mejor recomendado y el peor recomendado.
    Para cada profesor mostrado se asociados dos comentarios con mayoría
    de 'megusta' en notas_comentario, uno que tenga recomendacion y otro
    que no lo recomiende, ordenados por el que más 'megusta' tenga (AJAX).
    """
    response.generic_patterns = ['*.html']
    id_facultad = __validar_usuario()
    facultad = db.dependencia(id_facultad).nombre
    profesores = db(db.profesor.facultad == id_facultad).select(
      db.profesor.id,db.profesor.nombre,db.profesor.foto,
      db.profesor.slug,cache=(cache.ram, 3600),cacheable=True)
    profesores.setvirtualfields(conteo=CamposVirtualesProfesor())
    #top
    contar = db.profesor.id.count()
    mejor_profesor = db((db.profesor.facultad==id_facultad)&
                        (db.evaluacion.recomendable==True)).select(
                       db.profesor.id,contar,orderby=~contar,groupby=db.profesor.id,
                       left=db.evaluacion.on(db.profesor.id==db.evaluacion.evaluado),
                       limitby=(0,1),cache=(cache.ram, 600),cacheable=True).first()
    peor_profesor = db((db.profesor.facultad==id_facultad)&
                       (db.evaluacion.recomendable==False)).select(
                       db.profesor.id,contar,orderby=~contar,groupby=db.profesor.id,
                       left=db.evaluacion.on(db.profesor.id==db.evaluacion.evaluado),
                       limitby=(0,1),cache=(cache.ram, 600),cacheable=True).first()
    return dict(profesores=profesores.sort(lambda r: r.profesor.nombre.lower()),
                facultad=facultad,contar=contar,
                mejor_profesor=mejor_profesor,peor_profesor=peor_profesor)


def buscar():
    """
    Devuelve hasta 15 profesores que coincidan con la solicitud o
    ninguno si no hay coincidencias
    """
    response.generic_patterns = ['*.html']
    if request.vars.q:
        profesores = db(db.profesor.nombre.lower().contains(
          request.vars.q.lower())).select(
          db.profesor.ALL, orderby=db.profesor.nombre,
          limitby=(0,15),cache=(cache.ram, 3600))
        # si solo hay un profesor redirigir a el
        if len(profesores) == 1:
            profesor = profesores[0]
            redirect(URL('default', 'profesor', args=profesor.slug))
    else:
        profesores = None
    return dict(profesores=profesores,buscar=request.vars.q)


def profesor():
    """
    Todo lo relacionado con un profesor en particular se muestra aqui,
    junto con sus comentarios y formulario de comentario.
    Existen dos flujos para comentar: de usuarios registrados y de los anonimos.
    Las reglas para permitir un comentario con un usuario registrado
    es que solo hacer un comentario y una vez hecho modificarlo.
    Para el usuario anonimo es más complejo,
    primero ya que 2 filtros son necesarios: Sesión e IP, se comprueba
    que no haya un comentario hecho con este profesor en la misma IP, además
    de que en la sesión no este registrado un comentario, por si el usuario
    consigue llevar la sessión a un ambiente con IP nueva; en caso de que
    la sesión y la IP sean nuevas los comentarios son permitidos.
    Cada comentario aceptado debe almacenar en la session como diccionario:
    el id de la evaluacion, el id del profesor y la opción de migración,
    ésta es verdad cuando la sessión es anonima y falsa cuando es usuario registrado.
    """
    response.generic_patterns = ['*.html']
    if not request.args and __validar_usuario():
        redirect(URL('default', 'pasarela'))
    profesor = db(db.profesor.slug == request.args[0]).select(cacheable=True)
    if not profesor:
        raise HTTP(404, 'No hemos encontrado a ese profesor,\
        usa el ' + A('buscador', _href=URL('default', 'buscar')).xml())

    profesor.setvirtualfields(conteo=CamposVirtualesProfesor())
    profesor = profesor.first()
    comentarios = db(db.evaluacion.evaluado == profesor.profesor.id).select(
         db.evaluacion.id, db.evaluacion.recomendable,
         db.evaluacion.evento, db.evaluacion.comentario,
         db.evaluacion.evaluador, db.evaluacion.modificado_en,
         orderby=~db.evaluacion.modificado_en,cacheable=True)

    comentarios.setvirtualfields(notas=CamposVirtualesNotas())
    comentarios_positivos = comentarios.find(lambda r: r.evaluacion.recomendable == True)
    comentarios_negativos = comentarios.find(lambda r: r.evaluacion.recomendable == False)

    def agregar_comentario_sesion(id_comentario,id_profesor,importar):
        if session.evaluaciones is None: session.evaluaciones = []
        session.evaluaciones.append(dict(id_evaluacion=id_comentario,
                                         id_profesor=id_profesor,
                                         importar=importar))
    if auth.is_logged_in():
        #flujo de tratamiento si esta loggeado
        comentado = db((db.evaluacion.evaluador == auth.user_id) &
                       (db.evaluacion.evaluado == profesor.profesor.id)).select(cacheable=True).first()
        id_registro = comentado.id if comentado else None
        form = SQLFORM(db.evaluacion, id_registro, formstyle='divs', deleteable=True,
                   fields=['evento','comentario','evaluado','recomendable'],
                   _class="form-horizontal")
        if form.process().accepted:
            id_registro = form.vars.id
            # agregar a la session el comentario pero no importar
            agregar_comentario_sesion(form.vars.id, profesor.profesor.id, False)
            redirect(URL('default', 'profesor', args=profesor.profesor.slug,
                         anchor='evaluacion'+str(id_registro)))
        elif form.errors:
            response.flash = auth.user.first_name + ' asegurate de llenar ambos campos'
    else:
        #flujo de tratamiento si es anonimo
        id_registro = None
        form = SQLFORM(db.evaluacion, formstyle='divs',
                   fields=['evento','comentario','evaluado','recomendable'],
                   _class="form-horizontal")
        if form.validate():
            comentado_en_ip = db((db.evaluacion.ip == request.client) &
                           (db.evaluacion.evaluado == profesor.profesor.id)
                           ).select(cacheable=True).first()
            comentado_en_sesion = False
            if session.evaluaciones:
                comentado_en_sesion = any(
                  d['id_profesor'] == profesor.profesor.id for d in session.evaluaciones)

            if (comentado_en_ip is None) and (comentado_en_sesion is False):
                form.vars.id = db.evaluacion.insert(**dict(form.vars))
                agregar_comentario_sesion(form.vars.id, profesor.profesor.id, True)
                redirect(URL('default', 'profesor', args=profesor.profesor.slug,
                         anchor='evaluacion'+str(form.vars.id)))
            else:
                response.flash = SPAN('Demasiados comentarios anónimos, por favor ',B(
                                  A('Registrate',
                                 _href=URL('default', 'user',args='register',
                                           vars=dict(_next=URL(args=request.args))))))
                # guardar intento en la sesión
                agregar_comentario_sesion(0, profesor.profesor.id, False)
                """
                El único caso que no se prevenirá es cuando el usuario después de fallar
                borre su cookie y cambie de IP. La opción para prevenir es guardar la IP
                en la base de datos para después corroborar que no está en dicho registro
                pero esto produce más código
                y una consulta extra a la base de datos, algo excesivo. El captcha debería
                bastar para estimular el registro y desistir el abuso de comentarios
                anonimos.
                """
        elif form.errors:
            response.flash = 'Asegurate de llenar ambos campos correctamente'

    response.meta.description = 'Revisa y Recomienda a ' + profesor.profesor.nombre \
        + ' de la facultad de ' + profesor.profesor.facultad.nombre + ' en la ' + response.universidad
    response.meta.keywords = __keywords(profesor.profesor.nombre,
                                        profesor.profesor.facultad.nombre,
                                        response.universidad)
        
    return dict(profesor=profesor, form=form, id_registro=id_registro,
                comentarios_positivos=comentarios_positivos,
                comentarios_negativos=comentarios_negativos,captcha=__captcha_field())


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


@cache('sitemap',43200,cache.ram)
def sitemap():
    response.headers['Content-Type']='text/xml'
    # Adding Schemas for the site map
    xmlns='xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
    xmlnsImg='xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"\n'
    xmlnsVid='xmlns:video="http://www.google.com/schemas/sitemap-video/1.1"\n'
    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_xml +='<urlset %s %s %s>\n'%(xmlns,xmlnsImg,xmlnsVid)
     
    # Define Your Domain
    Domain = response.domain
    sitemap_xml += '<url>\n<loc>%s/</loc>\n<changefreq>daily</changefreq>\n<priority>0.8</priority>\n</url>\n' %(Domain)
    # Dynamic URLs From Tables For ex ... >> www.domain.com/post/1
    profesores = db(db.profesor).select(db.profesor.id,db.profesor.slug)
    for profesor in profesores:
        last_update = db(db.evaluacion.evaluado==profesor.id).select(db.evaluacion.modificado_en,orderby=db.evaluacion.modificado_en).first()
        if last_update:
            fecha = '<lastmod>%s</lastmod>\n' % last_update.modificado_en.isoformat()
        else:
            fecha = ''
        sitemap_xml += ('<url>\n'
                            '<loc>%s/profesor/%s</loc>\n'
                            '%s'
                            '<changefreq>weekly</changefreq>\n'
                            '<priority>0.5</priority>\n'
                        '</url>\n') %(Domain,profesor.slug,fecha)

    sitemap_xml +='</urlset>'
    return sitemap_xml
