# models.py

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


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
    detalles_editor = db.Column(db.JSON)  # <-- Cambiado a JSON para almacenar el editor de detalles
    tipo_consumo = db.Column(db.Enum('Desarrollo', 'Reuniones', 'Desarrollo por control de cambio', 'Soporte', 'Oportunidad de mejora', name='tipo_consumo'), nullable=False, default='Desarrollo')
    mes = db.Column(db.Enum(
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre', 
        name='meses'), 
        nullable=False, default='Enero'

    )

    facturada = db.Column(db.Boolean, default=False, nullable=False, server_default='0')
    cuenta_cobro_id = db.Column(db.Integer, nullable=True)

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
            'tipo_consumo': self.tipo_consumo,
            'mes': self.mes,
            'detalles_editor': self.detalles_editor,
            'facturada': self.facturada,
            'cuenta_cobro_id': self.cuenta_cobro_id
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
    contraseña = db.Column(db.String(256))  # Ampliado para hashes werkzeug
    empresa = db.Column(db.String(50))
    permisos = db.Column(db.String(20))
    otp_code = db.Column(db.String(6), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)

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
            'licencia': self.licencia
        }


# ── Módulo Cuenta de Cobros ─────────────────────────────────────────────────

class PerfilPago(db.Model):
    __tablename__ = 'perfil_pago'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), unique=True, nullable=False)
    nombres_completos = db.Column(db.String(150), nullable=False)
    documento = db.Column(db.String(20), nullable=False)
    tipo_cuenta = db.Column(db.Enum('Ahorros', 'Corriente', name='tipo_cuenta_banco'), nullable=False)
    banco = db.Column(db.String(100), nullable=False)
    numero_cuenta = db.Column(db.String(50), nullable=False)
    firma_texto = db.Column(db.String(200), nullable=True)
    firma_imagen = db.Column(db.Text, nullable=True)  # base64 PNG del canvas de firma
    fecha_actualizado = db.Column(db.DateTime, default=datetime.now)

    usuario = db.relationship('Usuarios', backref=db.backref('perfil_pago', uselist=False))

    def serialize(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'nombres_completos': self.nombres_completos,
            'documento': self.documento,
            'tipo_cuenta': self.tipo_cuenta,
            'banco': self.banco,
            'numero_cuenta': self.numero_cuenta,
            'firma_texto': self.firma_texto,
            'firma_imagen': bool(self.firma_imagen),  # no exponer el base64 en API
            'fecha_actualizado': self.fecha_actualizado.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_actualizado else None
        }


class CuentaCobro(db.Model):
    __tablename__ = 'cuenta_cobro'
    id = db.Column(db.Integer, primary_key=True)
    numero_cuenta = db.Column(db.String(20), unique=True, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    empresa_pagadora = db.Column(db.String(150), nullable=False)
    nit_pagadora = db.Column(db.String(20), nullable=False)
    concepto = db.Column(db.Text, nullable=True)
    valor_total = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    mes = db.Column(db.Enum(
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
        name='meses_cc'), nullable=False)
    anio = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.Enum(
        'PENDIENTE', 'REVISIÓN', 'APROBADA', 'PAGADA', 'RECHAZADA',
        name='estado_cuenta'), nullable=False, default='PENDIENTE')
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    fecha_pago = db.Column(db.DateTime, nullable=True)
    observacion_admin = db.Column(db.Text, nullable=True)

    usuario = db.relationship('Usuarios', backref='cuentas_cobro')
    detalles = db.relationship('DetalleCuentaCobro', backref='cuenta', lazy=True, cascade='all, delete-orphan')
    colillas = db.relationship('ColillaPago', backref='cuenta', lazy=True)
    confirmacion = db.relationship('ConfirmacionPago', backref='cuenta', uselist=False, lazy=True)

    def serialize(self):
        return {
            'id': self.id,
            'numero_cuenta': self.numero_cuenta,
            'usuario_id': self.usuario_id,
            'empresa_pagadora': self.empresa_pagadora,
            'nit_pagadora': self.nit_pagadora,
            'concepto': self.concepto,
            'valor_total': float(self.valor_total) if self.valor_total else 0,
            'mes': self.mes,
            'anio': self.anio,
            'estado': self.estado,
            'fecha_creacion': self.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_creacion else None,
            'fecha_pago': self.fecha_pago.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_pago else None,
            'observacion_admin': self.observacion_admin
        }


class DetalleCuentaCobro(db.Model):
    __tablename__ = 'detalle_cuenta_cobro'
    id = db.Column(db.Integer, primary_key=True)
    cuenta_cobro_id = db.Column(db.Integer, db.ForeignKey('cuenta_cobro.id'), nullable=False)
    tarea_id = db.Column(db.Integer, nullable=True)
    codigo_tarea = db.Column(db.String(50), nullable=False)
    titulo_tarea = db.Column(db.String(100), nullable=False)
    horas_dedicadas = db.Column(db.Float, nullable=False)
    precio_hora = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'cuenta_cobro_id': self.cuenta_cobro_id,
            'tarea_id': self.tarea_id,
            'codigo_tarea': self.codigo_tarea,
            'titulo_tarea': self.titulo_tarea,
            'horas_dedicadas': self.horas_dedicadas,
            'precio_hora': float(self.precio_hora) if self.precio_hora else 0,
            'subtotal': float(self.subtotal) if self.subtotal else 0
        }


class ColillaPago(db.Model):
    __tablename__ = 'colilla_pago'
    id = db.Column(db.Integer, primary_key=True)
    cuenta_cobro_id = db.Column(db.Integer, db.ForeignKey('cuenta_cobro.id'), nullable=False)
    archivo_nombre = db.Column(db.String(255), nullable=False)
    archivo_url = db.Column(db.String(500), nullable=False)
    subido_por = db.Column(db.String(100), nullable=False)
    fecha_subida = db.Column(db.DateTime, default=datetime.now)

    def serialize(self):
        return {
            'id': self.id,
            'cuenta_cobro_id': self.cuenta_cobro_id,
            'archivo_nombre': self.archivo_nombre,
            'archivo_url': self.archivo_url,
            'subido_por': self.subido_por,
            'fecha_subida': self.fecha_subida.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_subida else None
        }


class ConfirmacionPago(db.Model):
    __tablename__ = 'confirmacion_pago'
    id = db.Column(db.Integer, primary_key=True)
    cuenta_cobro_id = db.Column(db.Integer, db.ForeignKey('cuenta_cobro.id'), unique=True, nullable=False)
    confirmado = db.Column(db.Boolean, default=False, nullable=False)
    fecha_confirmacion = db.Column(db.DateTime, nullable=True)
    token_confirmacion = db.Column(db.String(100), unique=True, nullable=True)
    inconveniente = db.Column(db.Text, nullable=True)
    fecha_inconveniente = db.Column(db.DateTime, nullable=True)

    def serialize(self):
        return {
            'id': self.id,
            'cuenta_cobro_id': self.cuenta_cobro_id,
            'confirmado': self.confirmado,
            'fecha_confirmacion': self.fecha_confirmacion.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_confirmacion else None,
            'token_confirmacion': self.token_confirmacion,
            'inconveniente': self.inconveniente,
            'fecha_inconveniente': self.fecha_inconveniente.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_inconveniente else None
        }