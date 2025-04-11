from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length
from wtforms.validators import DataRequired, Length

class EmpresaForm(FlaskForm):
    nit = StringField('NIT', validators=[DataRequired(), Length(max=20)])
    empresa = StringField('Nombre de la Empresa', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Guardar')


class ProyectoForm(FlaskForm):
    empresa = StringField('Empresa', validators=[DataRequired(), Length(max=100)])
    codigo_proyecto = StringField('Código del Proyecto', validators=[DataRequired(), Length(max=50)])
    nombre_proyecto = StringField('Nombre del Proyecto', validators=[DataRequired(), Length(max=100)])
    descripcion_proyecto = TextAreaField('Descripción del Proyecto', validators=[DataRequired()])
    submit = SubmitField('Guardar')
