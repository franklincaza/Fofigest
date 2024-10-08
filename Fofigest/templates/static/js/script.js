function Filtros() {
    document.getElementById("filtros").innerHTML = `
        <form method="GET" action="/Reporte-Horas{{ session['empresa'] }}">
            <div class="row mb-4">
                <!-- Filtro de Estado -->
                <div class="col-sm-12 col-md-4 mb-2">
                    <label for="estado">Filtrar Estado</label>
                    <select class="form-control" id="estado" name="estado" onchange="this.form.submit();">
                        <option value="" {% if not estado %}selected{% endif %}>Todos los estados</option>
                        <option value="PENDIENTE" {% if estado == "PENDIENTE" %}selected{% endif %}>PENDIENTE</option>
                        <option value="PROGRESO" {% if estado == "PROGRESO" %}selected{% endif %}>PROGRESO</option>
                        <option value="REVISIÓN" {% if estado == "REVISIÓN" %}selected{% endif %}>REVISIÓN</option>
                        <option value="IMPEDIMENTOS" {% if estado == "IMPEDIMENTOS" %}selected{% endif %}>IMPEDIMENTOS</option>
                        <option value="COMPLETADOS" {% if estado == "COMPLETADOS" %}selected{% endif %}>COMPLETADOS</option>
                    </select>
                </div>

                <!-- Filtro de Responsable -->
                <div class="col-sm-12 col-md-4 mb-2">
                    <label for="responsable">Filtrar Responsable</label>
                    <select class="form-control" id="responsable" name="responsable" onchange="this.form.submit();">
                        <option value="" {% if not responsable %}selected{% endif %}>Todos los responsables</option>
                        {% for usuario in usuarios %}
                        <option value="{{ usuario.nombres }} {{ usuario.apellidos }}" {% if responsable == usuario.nombres %}selected{% endif %}>
                            {{ usuario.nombres }} {{ usuario.apellidos }}
                        </option>
                        {% endfor %}
                    </select>
                </div>

                <!-- Filtro de Proyecto -->
                <div class="col-sm-12 col-md-4 mb-2">
                    <label for="proyecto">Filtrar Proyecto</label>
                    <select class="form-control" id="proyecto" name="proyecto" onchange="this.form.submit();">
                        <option value="" {% if not proyecto_filtro %}selected{% endif %}>Todos los proyectos</option>
                        {% for proyecto_item in proyectos %}
                        <option value="{{ proyecto_item.codigo_proyecto }}" {% if proyecto_filtro == proyecto_item.codigo_proyecto %}selected{% endif %}>
                            {{ proyecto_item.nombre_proyecto }}
                        </option>
                        {% endfor %}
                    </select>
                </div>

                <!-- Filtro por Mes -->
                <div class="col-sm-12 col-md-4 mb-2">
                    <label for="mes">Filtrar por Mes</label>
                    <select class="form-control" id="mes" name="mes" onchange="this.form.submit();">
                        <option value="" {% if not mes %}selected{% endif %}>Todos los meses</option>
                        <option value="01" {% if mes == "01" %}selected{% endif %}>Enero</option>
                        <option value="02" {% if mes == "02" %}selected{% endif %}>Febrero</option>
                        <option value="03" {% if mes == "03" %}selected{% endif %}>Marzo</option>
                        <option value="04" {% if mes == "04" %}selected{% endif %}>Abril</option>
                        <option value="05" {% if mes == "05" %}selected{% endif %}>Mayo</option>
                        <option value="06" {% if mes == "06" %}selected{% endif %}>Junio</option>
                        <option value="07" {% if mes == "07" %}selected{% endif %}>Julio</option>
                        <option value="08" {% if mes == "08" %}selected{% endif %}>Agosto</option>
                        <option value="09" {% if mes == "09" %}selected{% endif %}>Septiembre</option>
                        <option value="10" {% if mes == "10" %}selected{% endif %}>Octubre</option>
                        <option value="11" {% if mes == "11" %}selected{% endif %}>Noviembre</option>
                        <option value="12" {% if mes == "12" %}selected{% endif %}>Diciembre</option>
                    </select>
                </div>

                <!-- Filtro por Fecha -->
                <div class="col-sm-12 col-md-4 mb-2">
                    <label for="fecha_inicio">Filtrar por Fecha de Inicio</label>
                    <input type="date" class="form-control" id="fecha_inicio" name="fecha_inicio" value="{{ request.args.get('fecha_inicio', '') }}" onchange="this.form.submit();">
                </div>

                <div class="col-sm-12 col-md-4 mb-2">
                    <label for="fecha_fin">Filtrar por Fecha de Fin</label>
                    <input type="date" class="form-control" id="fecha_fin" name="fecha_fin" value="{{ request.args.get('fecha_fin', '') }}" onchange="this.form.submit();">
                </div>
            </div>
        </form>
    `;
}
