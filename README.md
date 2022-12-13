# Acme-NFT

## ¿Cómo puedo desplegar el proyecto localmente?

Sólo debes seguir estos pasos:

- Instala [docker] y [git] en tu dispositivo
- Clona el repositorio en el directorio que desees con el comando:
```sh
git clone https://github.com/PGPI-G3-06/Acme-NFT.git
```
- Abre una terminal y dirígete al directorio donde se encuentra el repositorio clonado (no entres aún en la carpeta del proyecto) usando el comando ```cd {ruta}```
- Dirígete al directorio "docker/", dentro del repositorio. Para ello, desde el directorio en el que nos encontramos:
```sh
cd Acme-NFT/docker/
```
- Una vez dentro de este directorio, lanza el siguiente comando (el proceso puede tardar un rato):
```sh
docker-compose up -d
```

Este último comando creará las imágenes necesarias para el correcto funcionamiento de la aplicación junto con contenedores a partir de ellas (lanzados en segundo plano). Para asegurarse de que todo funciona correctamente, escriba en la terminal:
```sh
docker ps
```
La salida debe contener lo siguiente:
```sh
CONTAINER ID   IMAGE                   COMMAND                  CREATED          STATUS         PORTS                    NAMES
3e527c1c59c3   acme_nft_nginx:latest   "/docker-entrypoint.…"   20 minutes ago   Up 3 seconds   0.0.0.0:8000->80/tcp     acme_nft_nginx
0b25bfb71fcd   acme_nft_web:latest     "ash -c 'python mana…"   21 minutes ago   Up 3 seconds   5000/tcp                 acme_nft_web
d33d79a6446d   postgres:alpine         "docker-entrypoint.s…"   21 minutes ago   Up 4 seconds   0.0.0.0:5432->5432/tcp   acme_nft_db
```

En caso de ser así, el proyecto ya estará configurado de tal manera que, accediendo desde su navegador a <http://127.0.0.1:8000/>, puede navegar y utilizar el sistema de Acme-NFT. (El usuario creado por defecto es un administrador con credenciales: admin/admin)

## He terminado mi sesión ¿como cierro los contenedores?

Para cerrar los contenedores, diríjase desde la consola al directorio "docker/" del repositorio (en el que estábamos antes), y ejecute:

```sh
docker-compose down
```

Es importante encontrarse en este directorio porque el comando "docker-compose" busca el archivo "docker-compose.yml" para ordenar su hilo de ejecución (bien sea para crear o destruir)

## Nota final

A pesar de haber cerrado y eliminado los contenedores que necesita Acme-NFT para funcionar, las imágenes y volúmenes se mantendrán en su sistema. Haciendo uso de [Docker Desktop] puede eliminarlos con facilidad.

[docker]: <https://www.docker.com/products/docker-desktop/>
[Docker Desktop]: <https://www.docker.com/products/docker-desktop/>
[gitCLI]: <https://git-scm.com/downloads>