# -*- coding: utf-8 -*-

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

#from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
from gluon.tools import Auth, prettydate
auth = Auth(db)
#crud, service, plugins = Crud(db), Service(), PluginManager()

## campos extra
### Agregar en la proxima version la carrera
auth.settings.extra_fields['auth_user'] = [
  Field('facultad', 'reference dependencia'),
  Field('avatar', 'upload', autodelete=True, uploadseparate=True),
  Field('anonimo', 'boolean', default=True)]
## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = True
auth.settings.login_after_registration = True
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True
##el grupo por defecto para usuarios tipo 'normal'
if not db(db.auth_group).count():
    db.auth_group.insert(id=1, role='administrador', description='Super poderes')
    db.auth_group.insert(id=2, role='editor',
                         description='Editar profesores y eliminar comentarios')
    db.auth_group.insert(id=3, role='normal', description='Usuario común')
    auth.settings.everybody_group_id = 3
else:
    #normal_id = db.auth_group(db.auth_group.role == 'normal').id
    auth.settings.everybody_group_id = 3
## usuario anonimo por defecto
if not db(db.auth_user).count():
    db.auth_user.insert(id=1, first_name='anónimo', anonimo=True)

auth.settings.login_onaccept.append(lambda form: redirect(URL('pasarela')))
auth.settings.keep_session_onlogout = True
auth.settings.formstyle = 'divs'

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth, filename='private/janrain.key')

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
