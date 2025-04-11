from flask import Flask, request, jsonify
from datetime import datetime
import pandas as pd
from models import models    # Asegúrate de que models está correctamente configurado con SQLAlchemy y tu base de datos.

app = Flask(__name__)

@app.route('/masivosouttareas', methods=['POST'])
def crear_tarea():
    """
    Crear una nueva tarea.
    Se espera un JSON con los siguientes campos:
    - empresa, codigo_proyecto, codigo_tarea, titulo, descripcion, 
      fecha_inicio, responsable, horas_estimadas, estado (opcional), fecha_fin (opcional), fecha_facturacion (opcional)
    """
    data = request.get_json()

    nueva_tarea = models.Tareas(
        empresa=data['empresa'],
        codigo_proyecto=data['codigo_proyecto'],
        codigo_tarea=data['codigo_tarea'],
        titulo=data['titulo'],
        descripcion=data['descripcion'],
        fecha_inicio=datetime.strptime(data['fecha_inicio'], '%Y-%m-%d'),
        responsable=data['responsable'],
        horas_estimadas=data['horas_estimadas'],
        estado=data.get('estado', 'PENDIENTE'),
        fecha_fin=datetime.strptime(data['fecha_fin'], '%Y-%m-%d') if 'fecha_fin' in data else None,
        fecha_facturacion=datetime.strptime(data['fecha_facturacion'], '%Y-%m-%d') if 'fecha_facturacion' in data else None,
        mes=data['mes']
    )

    models.db.session.add(nueva_tarea)
    models.db.session.commit()

    return jsonify(nueva_tarea.serialize()), 201


def enviar_datos_desde_excel():
    # Cargar el archivo Excel
    file_excel = 'Task_Fofigest.xlsx'  # Asegúrate de que esté en el servidor Flask
    excel_data = pd.read_excel(file_excel)

    # Limpiar los espacios en las columnas
    excel_data.columns = excel_data.columns.str.strip()

    # Iterar sobre cada fila y enviar los datos a la ruta /outtareas
    for index, row in excel_data.iterrows():
        data = {
            "empresa": "SULFOQUIMICA SA",  # Valor predeterminado
            "codigo_proyecto": row['codigo_proyecto'],
            "codigo_tarea": int(row['codigo_tarea']),
            "titulo": row['titulo'],
            "descripcion": row['descripcion'],
            "fecha_inicio": str(row['fecha_inicio']),
            "responsable": row['responsable'],
            "horas_estimadas": int(row['horas_estimadas']),
            "estado": row.get('estado', 'PENDIENTE'),
            "fecha_fin": str(row['fecha_fin']) if pd.notna(row['fecha_fin']) else None,
            "fecha_facturacion": str(row['fecha_facturacion']) if pd.notna(row['fecha_facturacion']) else None,
            "mes": row['mes']
        }

        # Hacer una solicitud POST al endpoint /outtareas
        response = app.test_client().post('/outtareas', json=data)
        
        # Mostrar la respuesta del servidor
        print(f"Status code: {response.status_code}, Response: {response.json}")
enviar_datos_desde_excel()
if __name__ == '__main__':
    app.run(debug=True)
