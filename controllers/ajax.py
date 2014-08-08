# coding: utf8
def autocompletar_buscar():
    response.generic_patterns = ['*.json']
    if not URL.verify(request, hmac_key=KEY): raise HTTP(403)
    if not request.post_vars.q: raise HTTP(400)
    profesores = db(db.profesor.nombre.lower().contains(
          request.vars.q.lower())).select(
          db.profesor.nombre, limitby=(0,8))
    return dict(profesores=profesores)


@auth.requires_login()
def agregar_nota():
    if not request.vars.id_evaluacion or not request.vars.nota: raise HTTP(400)
    nota = request.vars.nota
    id_evaluacion = request.vars.id_evaluacion
    id_usuario = auth.user_id
    num_notas = int(request.vars.actual)
    clase = request.vars.clase
    nota_anterior = db((db.nota_evaluacion.id_usuario == id_usuario) &
                       (db.nota_evaluacion.id_evaluacion == id_evaluacion) &
                       (db.nota_evaluacion.nota == nota)
                       ).select(db.nota_evaluacion.id).first()
    if not nota_anterior:
        db.nota_evaluacion.insert(id_evaluacion=id_evaluacion,
                                  id_usuario=id_usuario,
                                  nota=nota)
        num_notas += 1
        #insertar
        return "jQuery('#"+nota+str(id_evaluacion)+"').attr('class', 'badge badge-warning');\
                 jQuery('#cuantos_"+nota+str(id_evaluacion)+"').html("+str(num_notas)+")"
    else:
        db(db.nota_evaluacion.id==nota_anterior.id).delete()
        num_notas -= 1
        #borrar
        #se restaura el color
        return "jQuery('#"+nota+str(id_evaluacion)+"').attr('class', '"+clase+"');\
                 jQuery('#cuantos_"+nota+str(id_evaluacion)+"').html("+str(num_notas)+")"
