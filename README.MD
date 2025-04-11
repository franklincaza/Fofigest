# Fofimatic - Gestión de Bolsa de Horas

Este proyecto es una aplicación web desarrollada en **Flask** para gestionar la bolsa de horas de los empleados de **Fofimatic**, una empresa de software. Se implementa utilizando el patrón **MVC** (Modelo-Vista-Controlador) para separar la lógica de la aplicación, la interfaz de usuario y la manipulación de datos.

## Estructura del Proyecto

El proyecto sigue el patrón MVC y tiene la siguiente estructura:


### Componentes del MVC

1. **Modelo** (`/models`):
   - Representa la lógica del negocio y la gestión de los datos. En este caso, se encargará de manejar la información relacionada con la bolsa de horas de los empleados.

2. **Vista** (`/templates`):
   - Las plantillas HTML que representan la interfaz gráfica del usuario. Utiliza Jinja2 para renderizar dinámicamente los datos en las vistas.

3. **Controlador** (`/controllers`):
   - Controla el flujo de datos entre el modelo y las vistas. Define las rutas de la aplicación y las acciones que se toman cuando los usuarios interactúan con la interfaz.

## Instalación y Configuración

### Requisitos

- **Python 3.8+**
- **Flask**
- **Jinja2** (ya viene integrado con Flask)
- Cualquier otro paquete necesario está listado en `requirements.txt`

### Pasos para instalar

1. Clonar el repositorio:

   ```bash
   git clone https://github.com/franklincaza/Fofigest.git
   cd fofimatic_project
   ``` 



