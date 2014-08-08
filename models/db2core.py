# -*- coding: utf-8 -*-

db.define_table('profesor',
                Field('nombre', length=128, notnull=True, unique=True),
                Field('foto', 'upload', autodelete=True, uploadseparate=True),
                Field('facultad', 'reference dependencia', ondelete='SET NULL'),
                Field('slug', compute=lambda r: IS_SLUG()(r.nombre+'-'+str(r.facultad))[0]),
                format='%(nombre)s')
## Esta tabla debe ser llenada por un administrador (por ahora)
db.profesor.nombre.required = True
db.profesor.nombre.writeable = False
db.profesor.nombre.represent = lambda nombre, registro: nombre.title()
db.profesor.foto.writeable = False
db.profesor.foto.requires = IS_IMAGE(minsize=(100,100))
db.profesor.facultad.writeable = False
db.profesor.slug.writeable = False

db.define_table('evaluacion',
                Field('recomendable', 'boolean',
                      required=True),
                Field('evento', length=32),
                Field('comentario', 'text'),
                Field('evaluado', 'reference profesor',
                      notnull=True),
                Field('evaluador', 'reference auth_user',
                      default=lambda: auth.user_id or 1),
                Field('ip', update=request.client),
                Field('modificado_en', 'datetime', update=request.now),
                Field('editado', 'boolean', update=True))
## el campo 'recomendable' se envia como campo oculto
db.evaluacion.evento.requires = [IS_NOT_EMPTY(), IS_LENGTH(minsize=5,maxsize=32)]
db.evaluacion.comentario.requires = [IS_NOT_EMPTY(), IS_LENGTH(minsize=8,maxsize=65536)]
db.evaluacion.evaluado.readeable = False
db.evaluacion.evaluado.writeable = False
db.evaluacion.evaluador.readeable = False
db.evaluacion.evaluador.writeable = False
db.evaluacion.evaluador.requires = None
db.evaluacion.ip.readeable = False
db.evaluacion.ip.writeable = False
db.evaluacion.modificado_en.writeable = False
db.evaluacion.editado.writeable = False
db.evaluacion.editado.readeable = False
## Eliminar las notas si el usuario actualiza su comentario
db.evaluacion._after_update.append(
  lambda s,f: db(db.nota_evaluacion.id_evaluacion == s.query.second).delete())

db.define_table('nota_evaluacion',
                Field('id_evaluacion', 'reference evaluacion'),
                Field('id_usuario', 'reference auth_user'),
                Field('nota', length=16, notnull=True, required=True),
                Field('creado_en', 'datetime', update=request.now))
db.nota_evaluacion.id_evaluacion.readeable = False
db.nota_evaluacion.id_evaluacion.writeable = False
db.nota_evaluacion.id_usuario.readeable = False
db.nota_evaluacion.id_usuario.writeable = False
db.nota_evaluacion.nota.requires = [IS_NOT_EMPTY(), IS_LENGTH(16), IS_IN_SET(['megusta', 'inapropiado'])]

# después de iniciar sessión agregar los comentarios anonimos
# que se hicieron a su cuenta
def agregar_comentarios_anonimos(formulario):
    if session.evaluaciones:
        for d in session.evaluaciones:
            if d['importar']:
                db.evaluacion(d['id_evaluacion']).update_record(evaluador=auth.user_id)
                d['importar'] = False
auth.settings.register_onaccept = agregar_comentarios_anonimos
