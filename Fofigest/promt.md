→ analiza el siguiente codigo flask y python:
```
# Tareas vista 
@app.route('/tareas', methods=['GET'])
@login_required
def vista_tareas():
    """
    Obtener todas las tareas con los filtros seleccionados por el usuario.
    """
    proyectos = models.Proyecto.query.all()
    usuarios = models.Usuarios.query.all()
    empresas = models.Empresas.query.all()
    tareas = models.Tareas.query.all()


    if request.method == 'POST':
    
        # Filtro por estado
        estado = request.form.get('estado')
        if estado:
            tareas_query = tareas_query.filter(models.Tareas.estado == estado)

        # Filtro por responsable
        responsable = request.form.get('responsable')
        if responsable:
            tareas_query = tareas_query.filter(models.Tareas.responsable == responsable)

        # Filtro por proyecto
        proyecto = request.form.get('proyecto')
        if proyecto:
            tareas_query = tareas_query.filter(models.Tareas.codigo_proyecto == proyecto)

        # Filtro por mes
        mes = request.form.get('mes')
        if mes:
            tareas_query = tareas_query.filter(models.Tareas.mes == mes)

        # Filtro por fecha de inicio y fecha de fin
        fecha_inicio = request.form.get('fecha_inicio_')
        fecha_fin = request.form.get('fecha_fin_')
        if fecha_inicio and fecha_fin:
            tareas_query = tareas_query.filter(models.Tareas.fecha_inicio >= fecha_inicio, 
                                            models.Tareas.fecha_fin <= fecha_fin)

        # Obtener el resultado final de las tareas filtradas
        tareas = tareas_query.all()

    # Calcular las horas estimadas y de ejecución
    #total_horas_estimadas = sum(tarea.horas_estimadas for tarea in tareas)
    total_horas_ejecucion = sum(tarea.horas_dedicadas for tarea in tareas)

    return render_template("tareas.html", tareas=tareas,
                                        empresas=empresas,
                                        proyectos=proyectos,
                                        usuarios=usuarios,
                                        total_horas_ejecucion=total_horas_ejecucion)
```
→ analiza el siguiente codigo html , jinja :
```
<!-- tareas.html -->
{% extends 'Base.html' %}
{% block content %}

<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined" />
<link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">

<div class="container-fluid bg-light py-5">
    <div class="card p-4 shadow">
        <div class="row mb-4">
            <div class="col-12 text-center">
                <h2 class="mb-3">TAREAS</h2>
            </div>
            <div class="d-flex gap-2 mb-3 justify-content-start align-items-center flex-wrap">
                <!-- Botón de refrescar --> 
                <a id="refrescar" class="btn btn-outline-primary d-flex align-items-center px-3" href="/tareas" onclick="window.location.reload();">
                    <span class="material-icons-outlined mr-2">refresh</span>
                    <span class="d-none d-md-inline">Refrescar</span>
                </a>
            
                <!-- Botón de descargar Excel -->
                <a class="btn btn-outline-success d-flex align-items-center px-3" href="/Reporte-HorasDownload{{ session['empresa'] }}">
                    <span class="material-icons-outlined mr-2">download</span>
                    <span class="d-none d-md-inline">Descargar Excel</span>
                </a>
            
                <!-- Botón de filtro -->
                <a class="btn btn-outline-secondary d-flex align-items-center px-3" data-toggle="modal" data-target="#filtroModal">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-funnel-fill mr-2" viewBox="0 0 16 16">
                        <path d="M1.5 1.5A.5.5 0 0 1 2 1h12a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-.128.334L10 8.692V13.5a.5.5 0 0 1-.342.474l-3 1A.5.5 0 0 1 6 14.5V8.692L1.628 3.834A.5.5 0 0 1 1.5 3.5z"/>
                    </svg>
                    <span class="d-none d-md-inline">Formulario</span>
                </a>

                <!-- Botón de agregar tarea -->
                {% if session['username'] == "admin" %}
                <button class="btn btn-outline-primary d-flex align-items-center px-3" data-toggle="modal" data-target="#tareasform" onclick="limpiarFormulario();generarCodigoUnico();">
                    <span class="material-icons-outlined mr-2">add</span>
                    <span class="d-none d-md-inline">Agregar Tarea</span>
                </button>
                {% endif %}
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
                            <form method="POST" action="/tareas">
                                <div class="row mb-4">
                                    <!-- Filtro de Estado -->
                                    <div class="col-sm-12 col-md-4 mb-2">
                                        <label for="estado">Filtrar Estado</label>
                                        <select class="form-control" id="estado" name="estado">
                                            <option value="">Todos los estados</option>
                                            <option value="PENDIENTE">PENDIENTE</option>
                                            <option value="PROGRESO">PROGRESO</option>
                                            <option value="REVISIÓN">REVISIÓN</option>
                                            <option value="IMPEDIMENTOS">IMPEDIMENTOS</option>
                                            <option value="COMPLETADOS">COMPLETADOS</option>
                                        </select>
                                    </div>
                    
                                    <!-- Filtro de Responsable -->
                                    <div class="col-sm-12 col-md-4 mb-2">
                                        <label for="responsable">Filtrar Responsable</label>
                                        <select class="form-control" id="responsable" name="responsable">
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
                                        <select class="form-control" id="proyecto" name="proyecto">
                                            <option value="">Todos los proyectos</option>
                                            {% for proyecto_item in proyectos %}
                                            <option value="{{ proyecto_item.codigo_proyecto }}">
                                                {{ proyecto_item.nombre_proyecto }}
                                            </option>
                                            {% endfor %}
                                        </select>
                                    </div>

                                    <!-- Filtro por Mes -->
                                    <div class="col-sm-12 col-md-4 mb-2">
                                        <label for="mes">Filtrar por Mes</label>
                                        <select class="form-control" id="mes" name="mes">
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

                                    <!-- Filtro por Fecha de Inicio -->
                                    <div class="col-sm-12 col-md-4 mb-2">
                                        <label for="fecha_inicio_">Filtrar por Fecha de Inicio</label>
                                        <input type="date" class="form-control" id="fecha_inicio_" name="fecha_inicio_">
                                    </div>

                                    <!-- Filtro por Fecha de Fin -->
                                    <div class="col-sm-12 col-md-4 mb-2">
                                        <label for="fecha_fin_">Filtrar por Fecha de Fin</label>
                                        <input type="date" class="form-control" id="fecha_fin_" name="fecha_fin_">
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

            <!-- Tabla de Tareas -->
            <div class="row">
                <div class="table-responsive">
                    <table class="table table-bordered table-striped table-hover" id="dataTable" width="100%" cellspacing="0">
                        <thead class="thead-dark">
                            <tr>
                                {% if session['username'] == "admin" %}
                                <th>ID</th>
                                {% endif %}
                                <th>TIPO DE CONSUMO</th>
                                <th>EMPRESA</th>
                                <th>CÓDIGO PROYECTO</th>
                                <th>CÓDIGO TAREA</th>
                                <th>TÍTULO</th>
                                <th>DESCRIPCIÓN</th>
                                <th>FECHA INICIO</th>
                                <th>FECHA FIN</th>
                                <th>HORAS DEDICADAS</th>
                                <th>HORAS ESTIMADAS</th>
                                <th>FECHA FACTURACIÓN</th>
                                <th>ESTADO</th>
                                <th>RESPONSABLE</th>
                                <th>MES</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for tarea in tareas %}
                            <tr>
                                {% if session['username'] == "admin" %}
                                <td class="position-relative" data-bs-toggle="modal" data-bs-target="#tareasform" onmouseover="showDeleteIcon({{ tarea.id }})" onmouseout="hideDeleteIcon({{ tarea.id }})">
                                    {{ tarea.id }}
                                    <span class="delete-icon material-icons-outlined position-absolute text-danger" id="delete-icon-{{ tarea.id }}" style="display: none; right: 5px; cursor: pointer;" onclick="event.stopPropagation(); eliminarTarea({{ tarea.id }})">delete</span>
                                </td>
                                {% endif %}
                                <td data-bs-toggle="modal" data-bs-target="#tareasform" onclick="editarTarea({{ tarea.id }})">{{ tarea.tipo_consumo }}</td>
                                <td data-bs-toggle="modal" data-bs-target="#tareasform" onclick="editarTarea({{ tarea.id }})">{{ tarea.empresa }}</td>
                                <td data-bs-toggle="modal" data-bs-target="#tareasform" onclick="editarTarea({{ tarea.id }})">{{ tarea.codigo_proyecto }}</td>
                                <td data-bs-toggle="modal" data-bs-target="#tareasform" onclick="editarTarea({{ tarea.id }})">{{ tarea.codigo_tarea }}</td>
                                <td data-bs-toggle="modal" data-bs-target="#tareasform" onclick="editarTarea({{ tarea.id }})">{{ tarea.titulo }}</td>
                                <td data-bs-toggle="modal" data-bs-target="#tareasform" onclick="editarTarea({{ tarea.id }})">{{ tarea.descripcion }}</td>
                                <td data-bs-toggle="modal" data-bs-target="#tareasform" onclick="editarTarea({{ tarea.id }})">{{ tarea.fecha_inicio }}</td>
                                <td data-bs-toggle="modal" data-bs-target="#tareasform" onclick="editarTarea({{ tarea.id }})">{{ tarea.fecha_fin }}</td>
                                <td data-bs-toggle="modal" data-bs-target="#tareasform" onclick="editarTarea({{ tarea.id }})">{{ tarea.horas_dedicadas }}</td>
                                <td data-bs-toggle="modal" data-bs-target="#tareasform" onclick="editarTarea({{ tarea.id }})">{{ tarea.horas_estimadas }}</td>
                                <td data-bs-toggle="modal" data-bs-target="#tareasform" onclick="editarTarea({{ tarea.id }})">{{ tarea.fecha_facturacion }}</td>

                                <!-- Columna ESTADO con botones -->
                                <td data-bs-toggle="modal" data-bs-target="#tareasform" onclick="editarTarea({{ tarea.id }})">
                                    <button class="btn 
                                        {% if tarea.estado == 'PENDIENTE' %}
                                            btn-secondary
                                        {% elif tarea.estado == 'PROGRESO' %}
                                            btn-primary
                                        {% elif tarea.estado == 'REVISIÓN' %}
                                            btn-warning text-dark
                                        {% elif tarea.estado == 'IMPEDIMENTOS' %}
                                            btn-danger
                                        {% elif tarea.estado == 'COMPLETADOS' %}
                                            btn-success
                                        {% endif %} 
                                        btn-sm text-center w-100">
                                        {{ tarea.estado }}
                                    </button>
                                </td>

                                <td data-bs-toggle="modal" data-bs-target="#tareasform" onclick="editarTarea({{ tarea.id }})">{{ tarea.responsable }}</td>
                                <td data-bs-toggle="modal" data-bs-target="#tareasform" onclick="editarTarea({{ tarea.id }})">{{ tarea.mes }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>



            <!-- Modal para Crear/Editar Tareas -->
            <div class="modal fade modal-fullscreen-xxl-down" id="tareasform" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Registrar tarea</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <!-- Formulario para Crear/Editar tareas -->
                            <form id="formTarea" method="POST">
                                <input type="hidden" id="tareaId" name="tareaId" />

                                <div class="form-group">
                                    <label for="empresa">Empresa</label>
                                    <select class="form-control" id="Cempresa" name="Cempresa" required>
                                        <option value="" disabled selected>Selecciona la empresa</option>
                                        {% for empresa in empresas %}
                                        <option value="{{ empresa.empresa }}">{{ empresa.empresa }}</option>
                                        {% endfor %}
                                    </select>
                                </div>

                                <div class="form-group">
                                    <label for="codigo_proyecto">Proyecto</label>
                                    <select class="form-control" id="codigo_proyecto" name="codigo_proyecto" required>
                                        <option value="" disabled selected>Selecciona el proyecto</option>
                                        {% for proyecto_item in proyectos %}
                                        <option value="{{ proyecto_item.nombre_proyecto }}">{{ proyecto_item.nombre_proyecto }}</option>
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
                                    <input type="number" class="form-control" id="horas_dedicadas" name="horas_dedicadas" value="0">
                                </div>
                                <div class="form-group">
                                    <label for="fecha_facturacion">Fecha Facturación</label>
                                    <input type="date" class="form-control" id="fecha_facturacion" name="fecha_facturacion">
                                </div>

                                <div class="form-group">
                                    <label for="estado">Estado</label>
                                    <!-- Botón que cambia de color dinámicamente según el estado seleccionado -->
                                    <div class="input-group">
                                        <button id="estadoButton" class="btn btn-secondary w-100 text-start" type="button" disabled>
                                            Selecciona un estado
                                        </button>
                                        <select class="form-control" id="Cestado" name="Cestado" required onchange="cambiarColorEstado()">
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
    const url = id ? `/tareas/${id}` : '/tareas';

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'  // Asegúrate de enviar JSON
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
<!-- Scripts de JavaScript de Bootstrap y jQuery -->
<script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.9.1/dist/umd/popper.min.js"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>

{% endblock %}

```
→ requiero poder hacer los filtros del formulario con todos los campos que esta en el formulario de filtros podrias ayudarme buscando una solucion.
