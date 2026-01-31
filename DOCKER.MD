# 🐳 Guía de Docker para Fofigest

Esta guía te enseñará desde cero cómo usar Docker para ejecutar la aplicación Fofigest.

## 📋 Tabla de Contenidos

1. [¿Qué es Docker?](#qué-es-docker)
2. [¿Por qué usar Docker?](#por-qué-usar-docker)
3. [Instalación de Docker](#instalación-de-docker)
4. [Conceptos básicos de Docker](#conceptos-básicos-de-docker)
5. [Ejecutar Fofigest con Docker](#ejecutar-fofigest-con-docker)
6. [Comandos útiles de Docker](#comandos-útiles-de-docker)
7. [Solución de problemas](#solución-de-problemas)

---

## 🤔 ¿Qué es Docker?

**Docker** es una plataforma de código abierto que permite crear, desplegar y ejecutar aplicaciones dentro de **contenedores**. Un contenedor es como una caja que empaqueta una aplicación con todas sus dependencias (bibliotecas, configuraciones, etc.) para que funcione de manera consistente en cualquier entorno.

### Analogía sencilla:
Imagina que Docker es como una maleta que contiene todo lo que necesitas para un viaje. No importa a dónde vayas, siempre tendrás todo lo necesario dentro de esa maleta.

---

## 💡 ¿Por qué usar Docker?

- **Portabilidad**: Ejecuta la aplicación en cualquier máquina que tenga Docker
- **Consistencia**: El mismo entorno en desarrollo, pruebas y producción
- **Aislamiento**: La aplicación no afecta ni es afectada por otras aplicaciones
- **Fácil instalación**: No necesitas instalar Python, librerías, ni configurar nada manualmente
- **Reproducibilidad**: Todos los desarrolladores trabajan con el mismo entorno

---

## 📥 Instalación de Docker

### Windows

1. **Descarga Docker Desktop**:
   - Ve a [Docker Desktop para Windows](https://www.docker.com/products/docker-desktop)
   - Descarga el instalador
   - Ejecuta el archivo descargado

2. **Instala Docker Desktop**:
   - Sigue el asistente de instalación
   - Acepta los términos y condiciones
   - Espera a que termine la instalación
   - Reinicia tu computadora si es necesario

3. **Verifica la instalación**:
   ```bash
   docker --version
   docker-compose --version
   ```

### macOS

1. **Descarga Docker Desktop**:
   - Ve a [Docker Desktop para Mac](https://www.docker.com/products/docker-desktop)
   - Descarga el instalador (Intel o Apple Silicon según tu Mac)

2. **Instala Docker Desktop**:
   - Abre el archivo `.dmg` descargado
   - Arrastra Docker a la carpeta de Aplicaciones
   - Abre Docker desde Aplicaciones

3. **Verifica la instalación**:
   ```bash
   docker --version
   docker-compose --version
   ```

### Linux (Ubuntu/Debian)

```bash
# Actualiza los paquetes existentes
sudo apt-get update

# Instala paquetes necesarios
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# Agrega la clave GPG oficial de Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Configura el repositorio
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instala Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Verifica la instalación
docker --version
docker compose version
```

---

## 📚 Conceptos básicos de Docker

### Imagen (Image)
Una **imagen** es una plantilla de solo lectura que contiene el código de la aplicación, las bibliotecas y las dependencias. Es como una receta para crear un contenedor.

### Contenedor (Container)
Un **contenedor** es una instancia en ejecución de una imagen. Es donde realmente se ejecuta tu aplicación. Puedes crear múltiples contenedores desde una misma imagen.

### Dockerfile
Un archivo de texto que contiene instrucciones para construir una imagen Docker. Define qué sistema operativo usar, qué software instalar, y cómo configurar la aplicación.

### Docker Compose
Una herramienta para definir y ejecutar aplicaciones Docker multi-contenedor usando un archivo YAML de configuración.

---

## 🚀 Ejecutar Fofigest con Docker

### Requisitos previos

- Tener Docker instalado (ver [sección de instalación](#instalación-de-docker))
- Tener el código fuente de Fofigest descargado

> **Nota técnica**: El contenedor Docker utiliza Python 3.10, que es compatible con todas las dependencias del proyecto. No necesitas instalar Python en tu máquina local.

### Método 1: Usando Docker Compose (Recomendado)

Este es el método más sencillo y recomendado para principiantes.

1. **Abre una terminal** en el directorio del proyecto Fofigest

2. **Construye y ejecuta el contenedor**:
   ```bash
   docker-compose up --build
   ```

3. **Accede a la aplicación**:
   - Abre tu navegador web
   - Ve a: `http://localhost:5000`
   - ¡Listo! La aplicación está funcionando

4. **Detener la aplicación**:
   - Presiona `Ctrl + C` en la terminal

5. **Ejecutar en segundo plano** (modo detached):
   ```bash
   docker-compose up -d
   ```

6. **Ver los logs**:
   ```bash
   docker-compose logs -f
   ```

7. **Detener y eliminar contenedores**:
   ```bash
   docker-compose down
   ```

### Modo desarrollo con Docker Compose

Si estás desarrollando y quieres que tus cambios se reflejen automáticamente sin reconstruir la imagen, crea un archivo `docker-compose.override.yml`:

```yaml
services:
  web:
    volumes:
      - .:/app
```

Este archivo se aplicará automáticamente sobre `docker-compose.yml` y montará tu código local en el contenedor.

### Método 2: Usando Docker directamente

Este método te da más control pero requiere ejecutar más comandos.

1. **Construir la imagen Docker**:
   ```bash
   docker build -t fofigest:latest .
   ```
   
   Explicación:
   - `docker build`: Comando para construir una imagen
   - `-t fofigest:latest`: Nombra la imagen como "fofigest" con etiqueta "latest"
   - `.`: Usa el Dockerfile en el directorio actual

2. **Ejecutar el contenedor**:
   ```bash
   docker run -d -p 5000:5000 --name fofigest-app fofigest:latest
   ```
   
   Explicación:
   - `docker run`: Ejecuta un contenedor desde una imagen
   - `-d`: Ejecuta en segundo plano (detached)
   - `-p 5000:5000`: Mapea el puerto 5000 del contenedor al puerto 5000 de tu máquina
   - `--name fofigest-app`: Nombra el contenedor como "fofigest-app"
   - `fofigest:latest`: Usa la imagen que acabamos de construir

3. **Accede a la aplicación**:
   - Abre tu navegador: `http://localhost:5000`

4. **Ver los logs del contenedor**:
   ```bash
   docker logs -f fofigest-app
   ```

5. **Detener el contenedor**:
   ```bash
   docker stop fofigest-app
   ```

6. **Iniciar el contenedor nuevamente**:
   ```bash
   docker start fofigest-app
   ```

7. **Eliminar el contenedor**:
   ```bash
   docker rm fofigest-app
   ```

---

## 🛠️ Comandos útiles de Docker

### Gestión de Contenedores

```bash
# Listar contenedores en ejecución
docker ps

# Listar todos los contenedores (incluyendo detenidos)
docker ps -a

# Detener un contenedor
docker stop <nombre-o-id-contenedor>

# Iniciar un contenedor detenido
docker start <nombre-o-id-contenedor>

# Reiniciar un contenedor
docker restart <nombre-o-id-contenedor>

# Eliminar un contenedor
docker rm <nombre-o-id-contenedor>

# Eliminar todos los contenedores detenidos
docker container prune

# Ejecutar un comando dentro de un contenedor
docker exec -it <nombre-contenedor> bash

# Ver los logs de un contenedor
docker logs <nombre-contenedor>

# Ver los logs en tiempo real
docker logs -f <nombre-contenedor>
```

### Gestión de Imágenes

```bash
# Listar todas las imágenes
docker images

# Eliminar una imagen
docker rmi <nombre-imagen>

# Eliminar imágenes sin usar
docker image prune

# Construir una imagen
docker build -t <nombre-imagen>:<etiqueta> .

# Ver el historial de una imagen
docker history <nombre-imagen>
```

### Docker Compose

```bash
# Construir y ejecutar servicios
docker-compose up --build

# Ejecutar en segundo plano
docker-compose up -d

# Detener servicios
docker-compose down

# Ver logs
docker-compose logs

# Ver logs en tiempo real
docker-compose logs -f

# Listar servicios en ejecución
docker-compose ps

# Reiniciar servicios
docker-compose restart

# Ejecutar un comando en un servicio
docker-compose exec web bash
```

### Limpieza del Sistema

```bash
# Eliminar todos los recursos no utilizados (contenedores, imágenes, redes, volúmenes)
docker system prune -a

# Ver el uso de espacio en disco
docker system df
```

---

## 🔍 Solución de problemas

### El puerto 5000 ya está en uso

**Problema**: `Error: bind: address already in use`

**Solución 1** - Cambiar el puerto en `docker-compose.yml`:
```yaml
ports:
  - "5001:5000"  # Usa el puerto 5001 en lugar de 5000
```

**Solución 2** - Detener el proceso que está usando el puerto:
```bash
# En Windows
netstat -ano | findstr :5000
taskkill /PID <numero-pid> /F

# En Linux/Mac
lsof -ti:5000 | xargs kill -9
```

### Error de permisos en Linux

**Problema**: `permission denied while trying to connect to the Docker daemon`

**Solución**:
```bash
# Agregar tu usuario al grupo docker
sudo usermod -aG docker $USER

# Aplicar los cambios
newgrp docker

# O reinicia tu sesión
```

### La imagen no se construye correctamente

**Problema**: Errores durante `docker build`

**Solución**:
```bash
# Limpia la caché de construcción
docker builder prune

# Construye sin usar caché
docker build --no-cache -t fofigest:latest .
```

### El contenedor se detiene inmediatamente

**Problema**: El contenedor se ejecuta y se detiene al instante

**Solución**:
```bash
# Ver los logs para identificar el error
docker logs <nombre-contenedor>

# Verificar que app.py tenga el código correcto para ejecutar Flask
```

### No se pueden instalar las dependencias

**Problema**: Error al instalar paquetes de `requirements.txt`

**Solución**:
```bash
# Asegúrate de que requirements.txt esté actualizado
pip freeze > requirements.txt

# Reconstruye la imagen sin caché
docker-compose build --no-cache
```

### Docker Desktop no inicia en Windows

**Problema**: Docker Desktop no arranca correctamente

**Solución**:
1. Verifica que la virtualización esté habilitada en la BIOS
2. Habilita WSL 2 (Windows Subsystem for Linux):
   ```powershell
   wsl --install
   wsl --set-default-version 2
   ```
3. Reinicia Docker Desktop

### Cambios en el código no se reflejan

**Problema**: Modificas el código pero no ves los cambios en el contenedor

**Solución**:
```bash
# Reconstruye la imagen y reinicia el contenedor
docker-compose up --build

# O con Docker directamente:
docker build -t fofigest:latest .
docker stop fofigest-app
docker rm fofigest-app
docker run -d -p 5000:5000 --name fofigest-app fofigest:latest
```

---

## 📖 Recursos adicionales

- [Documentación oficial de Docker](https://docs.docker.com/)
- [Docker Hub](https://hub.docker.com/) - Repositorio de imágenes Docker
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Cheat Sheet](https://www.docker.com/sites/default/files/d8/2019-09/docker-cheat-sheet.pdf)

---

## 🎯 Próximos pasos

Una vez que domines estos conceptos básicos, puedes explorar:

- **Volúmenes**: Para persistir datos entre reinicios de contenedores
- **Redes**: Para conectar múltiples contenedores
- **Variables de entorno**: Para configurar la aplicación
- **Multi-stage builds**: Para optimizar el tamaño de las imágenes
- **Docker en producción**: Despliegue en servidores reales

---

## ❓ ¿Necesitas ayuda?

Si tienes problemas o preguntas:
1. Revisa la sección de [Solución de problemas](#solución-de-problemas)
2. Consulta los logs del contenedor: `docker logs <nombre-contenedor>`
3. Busca el error en Google o Stack Overflow
4. Contacta al equipo de desarrollo

---

¡Felicidades! 🎉 Ya sabes cómo ejecutar Fofigest con Docker. Esta es una habilidad muy valiosa en el desarrollo moderno de software.
