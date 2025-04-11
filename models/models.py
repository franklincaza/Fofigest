# models.py

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# Initialize the SQLAlchemy instance
db = SQLAlchemy()

class Empresas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nit = db.Column(db.String(20), nullable=False, unique=True)
    empresa = db.Column(db.String(100), nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'nit': self.nit,
            'empresa': self.empresa
        }

class Proyecto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    empresa = db.Column(db.String(100), nullable=False)
    codigo_proyecto = db.Column(db.String(50), nullable=False, unique=True)
    nombre_proyecto = db.Column(db.String(100), nullable=False)
    descripcion_proyecto = db.Column(db.Text, nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'empresa': self.empresa,
            'codigo_proyecto': self.codigo_proyecto,
            'nombre_proyecto': self.nombre_proyecto,
            'descripcion_proyecto': self.descripcion_proyecto
        }

class Tareas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    empresa = db.Column(db.String(100), nullable=False)
    codigo_proyecto = db.Column(db.String(50), nullable=False)
    codigo_tarea = db.Column(db.String(50), nullable=False, unique=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)  # Se mantiene db.Text para permitir cualquier tamaño de texto
    fecha_inicio = db.Column(db.Date, nullable=False)  # Fecha de inicio del proyecto
    fecha_fin = db.Column(db.Date, nullable=True)  # Fecha de fin del proyecto
    responsable = db.Column(db.String(100), nullable=False)  # Responsable asignado a la tarea
    horas_dedicadas = db.Column(db.Float, nullable=False, default=0)  # Horas dedicadas
    horas_estimadas = db.Column(db.Float, nullable=False)  # Horas estimadas para completar la tarea
    fecha_facturacion = db.Column(db.Date, nullable=True)  # Fecha de facturación
    estado = db.Column(db.Enum('PENDIENTE', 'PROGRESO', 'REVISIÓN', 'IMPEDIMENTOS', 'COMPLETADOS', name='estado_tarea'), nullable=False, default='PENDIENTE')  # Estado de la tarea
    #porcentaje = db.Column(db.Float, nullable=False, default=0)
    tipo_consumo = db.Column(db.Enum('Desarrollo', 'Reuniones', 'Desarrollo por control de cambio', 'Soporte', 'Oportunidad de mejora', name='tipo_consumo'), nullable=False, default='Desarrollo')
    mes = db.Column(db.Enum(
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre', 
        name='meses'), 
        nullable=False, default='Enero'

    )

    def serialize(self):
        return {
            'id': self.id,
            'empresa': self.empresa,
            'codigo_proyecto': self.codigo_proyecto,
            'codigo_tarea': self.codigo_tarea,
            'titulo': self.titulo,
            'descripcion': self.descripcion,
            'fecha_inicio': self.fecha_inicio.strftime('%Y-%m-%d') if self.fecha_inicio else None,
            'fecha_fin': self.fecha_fin.strftime('%Y-%m-%d') if self.fecha_fin else None,
            'responsable': self.responsable,
            'horas_dedicadas': self.horas_dedicadas,
            'horas_estimadas': self.horas_estimadas,
            'fecha_facturacion': self.fecha_facturacion.strftime('%Y-%m-%d') if self.fecha_facturacion else None,
            'estado': self.estado,
            'tipo_consumo':self.tipo_consumo,
            'mes':self.mes
            #'porcentaje': self.porcentaje

        }

class SubTareas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo_tarea = db.Column(db.String(50), nullable=False)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'codigo_tarea': self.codigo_tarea,
            'titulo': self.titulo,
            'descripcion': self.descripcion
        }

class Usuarios(UserMixin,db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(50))
    apellidos = db.Column(db.String(50))
    correo = db.Column(db.String(100), unique=True)
    contraseña = db.Column(db.String(100))
    empresa = db.Column(db.String(50))
    permisos = db.Column(db.String(20))

    def serialize(self):
        return {
            'id': self.id,
            'nombres': self.nombres,
            'apellidos': self.apellidos,
            'empresa': self.empresa,
            'correo': self.correo,
            'permisos': self.permisos
        }


class Licencias(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nit = db.Column(db.String(20), nullable=False, unique=True)
    empresa = db.Column(db.String(100), nullable=False)
    licencia = db.Column(db.String(100), nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'nit': self.nit,
            'empresa': self.empresa,
            'licencia': self.licencia  # Corregido
        }