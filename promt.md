→ se un experto en js y html :
→ analiza este codigo 
```
{% extends 'Base.html' %}
{% block content %}

   <!-- BODY-->
   <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
   <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined" />
   <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
   
   <div class="container-fluid bg-light py-5">
       <div class="card p-4">
           <h2 class="text-center mb-4">TABLERO DE PROYECTOS</h2>
           
           <!-- Formulario de filtros -->
           <div class="d-flex gap-2 mb-3 justify-content-start align-items-center flex-wrap">
               <!-- Botón de refrescar --> 
               <a id="refrescar" class="btn btn-outline-primary d-flex align-items-center px-3" href="tablero" onclick="window.location.reload();">
                   <span class="material-icons-outlined mr-2">refresh</span>
                   <span class="d-none d-md-inline">Refrescar</span>
               </a>
           
               <!-- Botón de descargar filtro -->
               <a class="btn btn-outline-secondary d-flex align-items-center px-3" data-toggle="modal" data-target="#filtroModal">
                   <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-funnel-fill mr-2" viewBox="0 0 16 16">
                       <path d="M1.5 1.5A.5.5 0 0 1 2 1h12a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-.128.334L10 8.692V13.5a.5.5 0 0 1-.342.474l-3 1A.5.5 0 0 1 6 14.5V8.692L1.628 3.834A.5.5 0 0 1 1.5 3.5z"/>
                   </svg>
                   <span class="d-none d-md-inline">  Formulario   </span>
               </a>
           </div>

           <!-- Modal para el formulario de filtros -->
           <div class="modal fade" id="filtroModal" tabindex="-1" role="dialog" aria-labelledby="filtroModalLabel" aria-hidden="true">
               <div class="modal-dialog modal-lg" role="document">
                   <div class="modal-content">
                       <div class="modal-header">
                           <h5 class="modal-title" id="filtroModalLabel">Filtros de Reporte</h5>
                           <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                               <span aria-hidden="true">&times;</span>
                           </button>
                       </div>
                       <div class="modal-body">
                           <!-- Formulario de filtros dentro del modal -->
                           <form method="POST" action="tablero">
                               <div class="row mb-4">
                                   <!-- Filtro de Estado -->
                                   
                                   <!-- Filtro de Responsable -->
                                   <div class="col-sm-12 col-md-4 mb-2">
                                       <label for="responsable">Filtrar Responsable</label>
                                       <select class="form-control" id="responsable_" name="responsable_">
                                           <option value="">Todos los responsables</option>
                                           {% for usuario in usuarios %}
                                           <option value="{{ usuario.nombres }} {{ usuario.apellidos }}">
                                               {{ usuario.nombres }} {{ usuario.apellidos }}
                                           </option>
                                           {% endfor %}
                                       </select>
                                   </div>
               
                                   <!-- Filtro de Proyecto -->
                                   <div class="col-sm-12 col-md-4 mb-2">
                                       <label for="proyecto">Filtrar Proyecto</label>
                                       <select class="form-control" id="codigo_proyecto_" name="codigo_proyecto_">
                                           <option value="">Todos los proyectos</option>
                                           {% for proyecto_item in proyectos %}
                                           <option value="{{ proyecto_item.nombre_proyecto }}">
                                               {{ proyecto_item.nombre_proyecto }}
                                           </option>
                                           {% endfor %}
                                       </select>
                                   </div>

                                   <!-- Filtro por Mes -->
                                   <div class="col-sm-12 col-md-4 mb-2">
                                       <label for="mes">Filtrar por Mes</label>
                                       <select class="form-control" id="mes_" name="mes_">
                                           <option value="">Todos los meses</option>
                                           <option value="Enero">Enero</option>
                                           <option value="Febrero">Febrero</option>
                                           <option value="Marzo">Marzo</option>
                                           <option value="Abril">Abril</option>
                                           <option value="Mayo">Mayo</option>
                                           <option value="Junio">Junio</option>
                                           <option value="Julio">Julio</option>
                                           <option value="Agosto">Agosto</option>
                                           <option value="Septiembre">Septiembre</option>
                                           <option value="Octubre">Octubre</option>
                                           <option value="Noviembre">Noviembre</option>
                                           <option value="Diciembre">Diciembre</option>
                                       </select>
                                   </div>

                                 
                               </div>
                               <div class="modal-footer">
                                   <button type="button" class="btn btn-secondary" data-dismiss="modal">Cerrar</button>
                                   <button type="submit" class="btn btn-primary">Aplicar Filtros</button>
                               </div>
                           </form>
                       </div>
                   </div>
               </div>
           </div>
           
            <div class="row">
                <!-- Columna de PENDIENTE -->
                <div class="col-12 col-sm-6 col-md-4 col-lg-2 mb-3">
                    <h4 class="bg-secondary text-white text-center">PENDIENTE</h4>
                    <div class="kanban-column bg-light p-2" id="pendiente" data-estado="PENDIENTE" ondrop="drop(event)" ondragover="allowDrop(event)">
                        {% for tarea in tareas_PENDIENTE %}
                        <hr style="border: 1px solid black; width: 80%;">
                        <div class="kanban-item mb-2" draggable="true" ondragstart="drag(event)" id="{{ tarea.id }}">
                            <strong>{{ tarea.codigo_proyecto }}</strong> - {{ tarea.titulo }}<br>
                            <small>{{ tarea.descripcion }}</small><br>
                            <strong>Fecha Inicio:</strong> {{ tarea.fecha_inicio }}<br>
                            <strong>Fecha Fin:</strong> {{ tarea.fecha_fin }}<br>
                            <strong>Responsable:</strong> {{ tarea.responsable }}<br>
                            <strong>Horas dedicadas:</strong> {{ tarea.horas_dedicadas }}<br>
                            <strong>Horas estimadas:</strong> {{ tarea.horas_estimadas }}
                        </div>
                        <hr style="border: 1px solid black; width: 80%;">
                        {% endfor %}
                    </div>
                    <button class="btn btn-light btn-expand justify-content" data-bs-toggle="modal" data-bs-target="#tareasform" type="button" onclick="limpiarFormulario();generarCodigoUnico();">+ Agregar tarea</button>
                </div>

                <!-- Columna de PROGRESO -->
                <div class="col-12 col-sm-6 col-md-4 col-lg-2 mb-3">
                    <h4 class="bg-primary text-white text-center">PROGRESO</h4>
                    <div class="kanban-column bg-light p-2" id="progreso" data-estado="PROGRESO" ondrop="drop(event)" ondragover="allowDrop(event)">
                        {% for tarea in tareas_PROGRESO %}
                        <hr style="border: 1px solid black; width: 80%;">
                        <div class="kanban-item mb-2" draggable="true" ondragstart="drag(event)" id="{{ tarea.id }}">
                            <strong>{{ tarea.codigo_proyecto }}</strong> - {{ tarea.titulo }}<br>
                            <small>{{ tarea.descripcion }}</small><br>
                            <strong>Fecha Inicio:</strong> {{ tarea.fecha_inicio }}<br>
                            <strong>Fecha Fin:</strong> {{ tarea.fecha_fin }}<br>
                            <strong>Responsable:</strong> {{ tarea.responsable }}<br>
                            <strong>Horas dedicadas:</strong> {{ tarea.horas_dedicadas }}<br>
                            <strong>Horas estimadas:</strong> {{ tarea.horas_estimadas }}
                        </div>
                        <hr style="border: 1px solid black; width: 80%;">
                        {% endfor %}
                    </div>
                </div>

                <!-- Columna de REVISIÓN -->
                <div class="col-12 col-sm-6 col-md-4 col-lg-2 mb-3">
                    <h4 class="bg-warning text-dark text-center">REVISIÓN</h4>
                    <div class="kanban-column bg-light p-2" id="revision" data-estado="REVISIÓN" ondrop="drop(event)" ondragover="allowDrop(event)">
                        {% for tarea in tareas_REVISIÓN %}
                        <hr style="border: 1px solid black; width: 80%;">
                        <div class="kanban-item mb-2" draggable="true" ondragstart="drag(event)" id="{{ tarea.id }}">
                            <strong>{{ tarea.codigo_proyecto }}</strong> - {{ tarea.titulo }}<br>
                            <small>{{ tarea.descripcion }}</small><br>
                            <strong>Fecha Inicio:</strong> {{ tarea.fecha_inicio }}<br>
                            <strong>Fecha Fin:</strong> {{ tarea.fecha_fin }}<br>
                            <strong>Responsable:</strong> {{ tarea.responsable }}<br>
                            <strong>Horas dedicadas:</strong> {{ tarea.horas_dedicadas }}<br>
                            <strong>Horas estimadas:</strong> {{ tarea.horas_estimadas }}
                        </div>
                        <hr style="border: 1px solid black; width: 80%;">
                        {% endfor %}
                    </div>
                </div>

                <!-- Columna de IMPEDIMENTOS -->
                <div class="col-12 col-sm-6 col-md-4 col-lg-2 mb-3">
                    <h4 class="bg-danger text-white text-center">IMPEDIMENTOS</h4>
                    <div class="kanban-column bg-light p-2" id="impedimentos" data-estado="IMPEDIMENTOS" ondrop="drop(event)" ondragover="allowDrop(event)">
                        {% for tarea in tareas_IMPEDIMENTOS %}
                        <hr style="border: 1px solid black; width: 80%;">
                        <div class="kanban-item mb-2" draggable="true" ondragstart="drag(event)" id="{{ tarea.id }}">
                            <strong>{{ tarea.codigo_proyecto }}</strong> - {{ tarea.titulo }}<br>
                            <small>{{ tarea.descripcion }}</small><br>
                            <strong>Fecha Inicio:</strong> {{ tarea.fecha_inicio }}<br>
                            <strong>Fecha Fin:</strong> {{ tarea.fecha_fin }}<br>
                            <strong>Responsable:</strong> {{ tarea.responsable }}<br>
                            <strong>Horas dedicadas:</strong> {{ tarea.horas_dedicadas }}<br>
                            <strong>Horas estimadas:</strong> {{ tarea.horas_estimadas }}
                        </div>
                        <hr style="border: 1px solid black; width: 80%;">
                        {% endfor %}
                    </div>
                </div>
                {% if session['username'] == "admin" %} 
                <!-- Columna de COMPLETADOS -->
                <div class="col-12 col-sm-6 col-md-4 col-lg-2 mb-3">
                    <h4 class="bg-success text-white text-center">COMPLETADOS</h4>
                    <div class="kanban-column bg-light p-2" id="completados" data-estado="COMPLETADOS" ondrop="drop(event)" ondragover="allowDrop(event)">
                        {% for tarea in tareas_COMPLETADOS %}
                        <hr style="border: 1px solid black; width: 80%;">
                        <div class="kanban-item mb-2" draggable="true" ondragstart="drag(event)" id="{{ tarea.id }}">
                            <strong>{{ tarea.codigo_proyecto }}</strong> - {{ tarea.titulo }}<br>
                            <small>{{ tarea.descripcion }}</small><br>
                            <strong>Fecha Inicio:</strong> {{ tarea.fecha_inicio }}<br>
                            <strong>Fecha Fin:</strong> {{ tarea.fecha_fin }}<br>
                            <strong>Responsable:</strong> {{ tarea.responsable }}<br>
                            <strong>Horas dedicadas:</strong> {{ tarea.horas_dedicadas }}<br>
                            <strong>Horas estimadas:</strong> {{ tarea.horas_estimadas }}
                        </div>
                        <hr style="border: 1px solid black; width: 80%;">
                        {% endfor %}
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal para Crear/Editar Tareas -->
    <div class="modal fade" id="tareasform" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="exampleModalLabel">Registrar tarea</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" ></button>
            </div>
            <div class="modal-body">
              <!-- Formulario para Crear/Editar tareas -->
              <form id="formTarea" method="POST">
                <input type="hidden" id="tareaId" name="tareaId" />

                <div class="form-group">
                    <label for="Empresa">Empresa</label>
                <select class="form-control" id="Cempresa" name="Cempresa" required>
                    <option value="" disabled selected>Selecciona la empresa</option>
                    {% for empresa_item in empresas %}
                    <option value="{{empresa_item.empresa}}">{{ empresa_item.empresa }}</option>
                    {% endfor %}
                </select>
             </div>

                <div class="form-group">
                    <label for="Proyecto">Proyecto</label>
                <select class="form-control" id="codigo_proyecto" name="codigo_proyecto" required>
                    <option value="" disabled selected>Selecciona el proyecto</option>
                    {% for proyecto in proyectos %}
                    <option value="{{ proyecto.nombre_proyecto }}">{{ proyecto.nombre_proyecto }}</option>
                    {% endfor %}
                </select>
            </div>

                <div class="form-group">
                    <label for="codigo_tarea">Código Tarea</label>
                    <input type="text" class="form-control" id="codigo_tarea" name="codigo_tarea" onclick="generarCodigoUnico()" required>
                </div>
                <div class="form-group">
                    <label for="titulo">Título</label>
                    <input type="text" class="form-control" id="titulo" name="titulo" required>
                </div>
                <div class="form-group">
                    <label for="descripcion">Descripción</label>
                    <textarea class="form-control" id="descripcion" name="descripcion" required></textarea>
                </div>
                <div class="form-group">
                    <label for="fecha_inicio">Fecha Inicio</label>
                    <input type="date" class="form-control" id="fecha_inicio" name="fecha_inicio" required>
                </div>
                <div class="form-group">
                    <label for="fecha_fin">Fecha Fin</label>
                    <input type="date" class="form-control" id="fecha_fin" name="fecha_fin">
                </div>
                <div class="form-group">
                    <label for="horas_estimadas">Horas Estimadas</label>
                    <input type="number" class="form-control" id="horas_estimadas" name="horas_estimadas" required>
                </div>
                <div class="form-group">
                    <label for="horas_dedicadas">Horas Dedicadas</label>
                    <input type="number" class="form-control" id="horas_dedicadas" name="horas_dedicadas" required>
                </div>
                <div class="form-group">
                    <label for="estado">Estado</label>
                    <!-- Botón que cambia de color dinámicamente según el estado seleccionado -->
                    <div class="input-group">
                        <button id="estadoButton" class="btn btn-secondary w-100 text-start" type="button" disabled>
                            Selecciona un estado
                        </button>
                        <select class="form-control" id="Cestado" name="Cestado" required onchange="cambiarColorEstado()" required>
                            <option value="" disabled selected>Selecciona un estado</option>
                            <option value="PENDIENTE">PENDIENTE</option>
                            <option value="PROGRESO">PROGRESO</option>
                            <option value="REVISIÓN">REVISIÓN</option>
                            <option value="IMPEDIMENTOS">IMPEDIMENTOS</option>
                            {% if session['username'] == "admin" %} 
                            <option value="COMPLETADOS">COMPLETADOS</option>
                            {% endif %}
                        </select>
                    </div>
                </div>
                
                <script>
                    function cambiarColorEstado() {
                        const estadoSelect = document.getElementById("Cestado");
                        const estadoButton = document.getElementById("estadoButton");
                        const selectedEstado = estadoSelect.value;
                
                        // Reiniciar clases de botón
                        estadoButton.className = "btn w-100 text-start";
                
                        // Aplicar la clase correcta según el estado seleccionado
                        switch (selectedEstado) {
                            case 'PENDIENTE':
                                estadoButton.classList.add('btn-secondary');
                                break;
                            case 'PROGRESO':
                                estadoButton.classList.add('btn-primary');
                                break;
                            case 'REVISIÓN':
                                estadoButton.classList.add('btn-warning', 'text-dark');
                                break;
                            case 'IMPEDIMENTOS':
                                estadoButton.classList.add('btn-danger');
                                break;
                            case 'COMPLETADOS':
                                estadoButton.classList.add('btn-success');
                                break;
                            default:
                                estadoButton.classList.add('btn-secondary');
                        }
                
                        // Cambiar el texto del botón al estado seleccionado
                        estadoButton.textContent = selectedEstado;
                    }
                </script>
                
                <div class="form-group">
                    <label for="responsable">Responsable</label>
                    <select class="form-control" id="Cresponsable" name="Cresponsable" required>
                        <option value="" disabled selected>Selecciona el responsable</option>
                        {% for usuario in usuarios %}
                        <option value="{{ usuario.nombres }} {{ usuario.apellidos }}">{{ usuario.nombres }} {{ usuario.apellidos }}</option>
                        {% endfor %}
                    </select>
                </div>

                <div class="form-group">
                    <label for="responsable">Tipo de consumo</label>
                    <select class="form-control" id="consumo" name="consumo" required>
                        <option value="" disabled selected>Selecciona el tipo de consumo</option>
                        <option value="Reuniones" selected>Reuniones</option>
                        <option value="Desarrollo">Desarrollo</option>
                        <option value="Desarrollo por control de cambio">Desarrollo por control de cambio</option>
                        <option value="Soporte">Soporte</option>
                        <option value="Oportunidad de mejora">Oportunidad de mejora</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="mes">Mes</label>
                    <select class="form-control" id="mes" name="mes" required>
                        <option value="" disabled selected>Selecciona el mes</option>
                        <option value="Enero">Enero</option>
                        <option value="Febrero">Febrero</option>
                        <option value="Marzo">Marzo</option>
                        <option value="Abril">Abril</option>
                        <option value="Mayo">Mayo</option>
                        <option value="Junio">Junio</option>
                        <option value="Julio">Julio</option>
                        <option value="Agosto">Agosto</option>
                        <option value="Septiembre">Septiembre</option>
                        <option value="Octubre">Octubre</option>
                        <option value="Noviembre">Noviembre</option>
                        <option value="Diciembre">Diciembre</option>
                    </select>
                </div>

                <div class="modal-footer">
                    <button type="submit" class="btn btn-primary">Guardar</button>
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                </div>
              </form>
            </div>
          </div>
        </div>
    </div>

    <script>
        function showDeleteIcon(id) {
            document.getElementById('delete-icon-' + id).style.display = 'inline';
        }
    
        function hideDeleteIcon(id) {
            document.getElementById('delete-icon-' + id).style.display = 'none';
        }
    
        function editarTarea(id) {
            // Obtener los detalles de la tarea por ID y rellenar el formulario para editar
            fetch(`/tareas/${id}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('tareaId').value = data.id;
                document.getElementById('Cempresa').value = data.empresa;
                document.getElementById('codigo_proyecto').value = data.codigo_proyecto;
                document.getElementById('codigo_tarea').value = data.codigo_tarea;
                document.getElementById('titulo').value = data.titulo;
                document.getElementById('descripcion').value = data.descripcion;
                document.getElementById('fecha_inicio').value = data.fecha_inicio;
                document.getElementById('fecha_fin').value = data.fecha_fin || '';
                document.getElementById('horas_estimadas').value = data.horas_estimadas;
                document.getElementById('horas_dedicadas').value = data.horas_dedicadas;
                document.getElementById('fecha_facturacion').value = data.fecha_facturacion || '';
                document.getElementById('Cestado').value = data.estado;
                document.getElementById('Cresponsable').value = data.responsable;
                document.getElementById('consumo').value = data.tipo_consumo;
                document.getElementById('mes').value = data.mes;
            });
        }
    
        document.getElementById('formTarea').addEventListener('submit', function(event) {
            event.preventDefault();
    
            const id = document.getElementById('tareaId').value;
            const method = id ? 'PUT' : 'POST';  // Usar PUT si es edición, POST si es creación
            const url = id ? `/tareas/${id}` : '/outtareas';
    
            fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    empresa: document.getElementById('Cempresa').value,
                    codigo_proyecto: document.getElementById('codigo_proyecto').value,
                    codigo_tarea: document.getElementById('codigo_tarea').value,
                    titulo: document.getElementById('titulo').value,
                    descripcion: document.getElementById('descripcion').value,
                    fecha_inicio: document.getElementById('fecha_inicio').value,
                    fecha_fin: document.getElementById('fecha_fin').value,
                    horas_estimadas: document.getElementById('horas_estimadas').value,
                    horas_dedicadas: document.getElementById('horas_dedicadas').value,
                    estado: document.getElementById('Cestado').value,
                    responsable: document.getElementById('Cresponsable').value,
                    tipo_consumo: document.getElementById('consumo').value,
                    mes: document.getElementById('mes').value
                })
            })
            .then(response => {
                if (response.ok) {
                    Swal.fire(
                        '¡Éxito!',
                        'La tarea ha sido guardada correctamente.',
                        'success'
                    ).then(() => {
                        location.reload();
                    });
                } else {
                    Swal.fire(
                        'Error',
                        'Ocurrió un problema al guardar la tarea.',
                        'error'
                    );
                }
            });
        });
    
        function limpiarFormulario() {
            document.getElementById('formTarea').reset();
            document.getElementById('tareaId').value = '';
        }
    
        function generarCodigoUnico() {
            const now = new Date();
            const timestamp = now.getFullYear().toString() + 
                              (now.getMonth() + 1).toString().padStart(2, '0') + 
                              now.getDate().toString().padStart(2, '0') + 
                              now.getHours().toString().padStart(2, '0') + 
                              now.getMinutes().toString().padStart(2, '0') + 
                              now.getSeconds().toString().padStart(2, '0') + 
                              now.getMilliseconds().toString().padStart(3, '0');
            
            const randomPart = Math.random().toString(36).substring(2, 10);
    
            const uniqueCode = `${timestamp}-${randomPart}`;
    
            document.getElementById('codigo_tarea').value = uniqueCode;  // Asignar el código al input de 'codigo'
            return uniqueCode;
        }
    
        {% if session['username'] == "admin" %}
    
        function eliminarTarea(id) {
            Swal.fire({
                title: '¿Estás seguro?',
                text: "¡No podrás revertir esto!",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Sí, eliminar'
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch(`/tareas/${id}`, {
                        method: 'DELETE'
                    })
                    .then(response => {
                        if (response.ok) {
                            Swal.fire(
                                '¡Eliminado!',
                                'La tarea ha sido eliminada.',
                                'success'
                            ).then(() => {
                                location.reload();
                            });
                        } else {
                            Swal.fire(
                                'Error',
                                'Ocurrió un problema al eliminar la tarea.',
                                'error'
                            );
                        }
                    });
                }
            });
        }
    
        {% else %}
    
        function eliminarTarea(id) {
            Swal.fire(
                'Acceso Denegado',
                'No tienes permisos para borrar tareas.',
                'error'
            );
        }
    
        {% endif %}
    </script>
    
     <!-- Scripts de Bootstrap y dependencias -->
     <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
     <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.6/dist/umd/popper.min.js"></script>
     <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    

{% endblock %}
```
→ analiza esta funcion que fue realizada en bakend en flask :
```
# Tareas 
@app.route('/actualizar_estado_tarea/<int:tarea_id>', methods=['POST'])
def actualizar_estado_tarea(tarea_id):
    data = request.get_json()
    nuevo_estado = data.get('nuevo_estado')

    # Obtener la tarea por ID
    tarea = models.Tareas.query.get_or_404(tarea_id)

    # Validar que el nuevo estado es válido
    if nuevo_estado not in ['PENDIENTE', 'PROGRESO', 'REVISIÓN', 'IMPEDIMENTOS', 'COMPLETADOS']:
        return jsonify({'message': 'Estado inválido'}), 400

    # Actualizar el estado de la tarea
    tarea.estado = nuevo_estado

    # Guardar cambios en la base de datos
    try:
        models.db.session.commit()
        return jsonify({'message': 'Estado actualizado correctamente'}), 200
    except Exception as e:
        models.db.session.rollback()
        return jsonify({'message': 'Error al actualizar el estado'}), 500

```
→ sin modificar funcionalidades del html ni apesto visual añadele la funcionalidad de arrastre de tareas  y que automaticamente se actualize la tarea.
→ generar un scripr completo con la solucion que me permita copiar y pegarlo en mi proyecto.
→ que sea completamente funcional el codigo html, y generar una salida completa no resumida , para poder copiar y pegar en mi proyecto.
