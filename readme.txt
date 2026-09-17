============================================================
  CARGUE CEDER - GUIA DE INSTALACION EN WINDOWS PASO A PASO
============================================================

Esta guia explica como dejar funcionando el sitio desde cero
en un servidor Windows, clonando el repositorio desde GitHub
por SSH, y dejando la URL como:  http://cargueceder:5000


------------------------------------------------------------
PASO 1 - Instalar Python
------------------------------------------------------------
1. Ve a:  https://www.python.org/downloads/windows/
2. Descarga la ultima version de Python (3.10 o 3.12).
3. Ejecuta el instalador.
4. IMPORTANTE: marca la casilla  "Add Python to PATH"
   (esta abajo, antes del boton Install Now).
5. Click en "Install Now" y espera que termine.

Para verificar, abre CMD (tecla Windows + "cmd" + Enter) y escribe:
   python --version
Debe mostrar la version de Python (ej: Python 3.12.1).


------------------------------------------------------------
PASO 2 - Instalar Git
------------------------------------------------------------
1. Ve a:  https://git-scm.com/download/win
2. Descarga e instala con las opciones por defecto
   (siguiente, siguiente, finalizar).

Para verificar, en CMD escribe:
   git --version
Debe mostrar la version de Git.


------------------------------------------------------------
PASO 3 - Generar la llave publica SSH del servidor
------------------------------------------------------------
En CMD escribe:
   ssh-keygen -t ed25519 -C "tu-correo@tucorreo.com"

Cuando pregunte, presiona Enter 3 veces
(dos preguntas de passphrase, la puedes dejar vacia).

Para ver la llave publica, escribe:
   type C:\Users\TU_USUARIO\.ssh\id_ed25519.pub

Se imprimira un texto largo que empieza con:
   ssh-ed25519 AAAA...
COPIALO COMPLETO (desde "ssh-ed25519" hasta el final).

NOTA: reemplaza TU_USUARIO por el nombre de la carpeta de tu
usuario en Windows (la ves al hacer "whoami" en CMD).


------------------------------------------------------------
PASO 4 - Registrar la llave en GitHub
------------------------------------------------------------
1. Abre el navegador y entra a:
   https://github.com/settings/keys
   (debes estar logueado en tu cuenta de GitHub).
2. Click en el boton verde  "New SSH key".
3. En "Title" escribe un nombre, por ejemplo:  Servidor Windows
4. En "Key" pega el texto de la llave que copiaste en el PASO 3.
5. Click en "Add SSH key".

Para comprobar que funciono, en CMD escribe:
   ssh -T git@github.com

Debe mostrar:
   Hi hgrestrepor! You've successfully authenticated, but GitHub
   does not provide shell access.

Si te pregunta "Are you sure you want to continue connecting",
escribe  yes  y Enter.


------------------------------------------------------------
PASO 5 - Clonar el repositorio (por SSH)
------------------------------------------------------------
En CMD, escribe:

   git clone git@github.com:hgrestrepor/cargue-masivo-contapymes.git
   cd cargue-masivo-contapymes

(Si NO funciona el SSH, una opcion segura es clonar por HTTP:
   git clone https://github.com/hgrestrepor/cargue-masivo-contapymes.git
   cd cargue-masivo-contapymes
)
Quedaras dentro de la carpeta del proyecto.


------------------------------------------------------------
PASO 6 - Instalar las librerias (dependencias)
------------------------------------------------------------
Desde la carpeta del proyecto, en CMD escribe:

   pip install -r requirements.txt

Esto instala: flask, bcrypt, pandas, openpyxl y requests.

Para comprobar que todo quedo instalado, escribe:
   pip list
Debes ver entre la lista: Flask, pandas, bcrypt, openpyxl y requests.


------------------------------------------------------------
PASO 7 - Iniciar el servidor la primera vez
------------------------------------------------------------
Desde la carpeta del proyecto, en CMD escribe:

   python app.py

Al arrancar por primera vez la aplicacion:
   - crea la base de datos users.db automaticamente
   - crea el usuario administrador automaticamente

Veras en pantalla:
   Servidor iniciado!
   URL: http://localhost:5000
   Admin: adminceder / AdminCeder345

Deja esa ventana de CMD abierta (puedes minimizarla).
CREDENCIALES DE ACCESO:
   Usuario   : adminceder
   Contrasena: AdminCeder345


------------------------------------------------------------
PASO 8 - Entrar al sitio
------------------------------------------------------------
Abre el navegador y entra a:

   http://localhost:5000

Ingresa con el usuario y la contrasena del Paso 7.


------------------------------------------------------------
PASO 9 (OPCIONAL) - Alias de URL: cargueceder:5000
------------------------------------------------------------
Para que la pagina quede como  http://cargueceder:5000
en vez de http://localhost:5000, se edita el archivo HOSTS
de Windows:

1. Abre el Bloc de notas como Administrador:
   - click derecho sobre "Bloc de notas" -> "Ejecutar como administrador"

2. En el Bloc de notas:  Archivo -> Abrir
3. En "Nombre de archivo" pega esta ruta y Enter:
   C:\Windows\System32\drivers\etc\hosts
4. Cambia el tipo de archivo de "Documentos de texto (*.txt)"
   a "Todos los archivos (*)" para que aparezca el archivo hosts.
5. Abre el archivo hosts.

6. Al FINAL del archivo agregale esta linea (sin #):
   127.0.0.1       cargueceder

7. Guarda el archivo (Ctrl+S).

8. Verifica que resolvio. En CMD escribe:
   ping cargueceder

Debe responder desde 127.0.0.1.

9. Con el servidor corriendo, entra desde el navegador a:
   http://cargueceder:5000

Ya quedara funcionando con la nueva URL.
Si el alias no responde, en CMD ejecuta:  ipconfig /flushdns


------------------------------------------------------------
PASO 10 - Como iniciar la proxima vez
------------------------------------------------------------
Cada vez que reinicies el servidor:
   - con la ventana del proyecto abierta:   python app.py
   - y entra a: http://cargueceder:5000   (o http://localhost:5000)

TAMBIEN puedes usar el archivo iniciar.bat incluido en el proyecto,
que instala dependencias y arranca la aplicacion automaticamente:
   - doble click sobre  iniciar.bat


------------------------------------------------------------
SOLUCION DE PROBLEMAS
------------------------------------------------------------
- "python no se reconoce": reinstala Python marcando
  "Add Python to PATH", o usa el comando  py app.py

- "Permission denied (publickey)" al clonar: volver al PASO 4
  y confirmar que la llave quedo bien pegada, y que
  "ssh -T git@github.com" funcione.

- "Puerto 5000 en uso": en CMD:
      netstat -ano | findstr :5000
      taskkill /PID <NUMERO_DEL_PID> /F

- El alias cargueceder no abre: revisar el archivo hosts
  (PASO 9, punto 6) que este la linea  127.0.0.1 cargueceder,
  guardado como administrador.

- Para actualizar el sitio con cambios nuevos: git pull  y
  reiniciar el servidor.

============================================================
 Fin de la guia
============================================================