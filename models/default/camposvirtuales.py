# -*- coding: utf-8 -*-

# campos virtuales para profesores
class CamposVirtualesProfesor(object):
    def comentarios(self):
        return db(db.evaluacion.evaluado==self.profesor.id).count(cache=(cache.ram, 15))
    def recomendaciones(self):
        return db((db.evaluacion.evaluado==self.profesor.id) &
                  (db.evaluacion.recomendable==True)).count(cache=(cache.ram, 15))
    def top_positivo(self):
        return db((db.nota_evaluacion.id_evaluacion==db.evaluacion.id) &
                  (db.evaluacion.evaluado==self.profesor.id) &
                  (db.nota_evaluacion.nota=='megusta') &
                  (db.evaluacion.recomendable==True)
                  ).select(db.evaluacion.evento,
                           db.evaluacion.comentario,
                           groupby=db.evaluacion.id,
                           orderby=~db.evaluacion.id.count(),
                           cache=(cache.ram, 300)
                           ).first()
    def top_negativo(self):
        return db((db.nota_evaluacion.id_evaluacion==db.evaluacion.id) &
                  (db.evaluacion.evaluado==self.profesor.id) &
                  (db.nota_evaluacion.nota=='megusta') &
                  (db.evaluacion.recomendable==False)
                  ).select(db.evaluacion.evento,
                           db.evaluacion.comentario,
                           groupby=db.evaluacion.id,
                           orderby=~db.evaluacion.id.count(),
                           cache=(cache.ram, 300)
                           ).first()


class CamposVirtualesNotas(object):
    def cuantos_megusta(self):
        return db((db.nota_evaluacion.id_evaluacion == self.evaluacion.id) &
                   (db.nota_evaluacion.nota == 'megusta')
                   ).count(cache=(cache.ram, 600))

    def tiene_megusta(self):
        if auth.is_logged_in():
            return db((db.nota_evaluacion.id_usuario == auth.user_id) &
                       (db.nota_evaluacion.id_evaluacion == self.evaluacion.id) &
                       (db.nota_evaluacion.nota == 'megusta')
                       ).count()
        else:
            return 0

    def cuantos_inapropiado(self):
        return db((db.nota_evaluacion.id_evaluacion == self.evaluacion.id) &
                   (db.nota_evaluacion.nota == 'inapropiado')
                   ).count(cache=(cache.ram, 600))

    def tiene_inapropiado(self):
        if auth.is_logged_in():
            return db((db.nota_evaluacion.id_usuario == auth.user_id) &
                       (db.nota_evaluacion.id_evaluacion == self.evaluacion.id) &
                       (db.nota_evaluacion.nota == 'inapropiado')
                       ).count()
        else:
            return 0
