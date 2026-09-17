# Cargue Masivo ContaPymes (Cargue Ceder)

Aplicación web (Flask) para cargar de forma masiva archivos Excel de **Madres** y **Transportes**, transformarlos a JSON y enviarlos al endpoint de ContaPymes.

Desarrollada y probada en Linux, pero funciona igual en **Windows Server / Windows 10/11**.

---

## 1. Requisitos previos en el servidor Windows

Instalar en este orden:

1. **Python 3.9 o superior (recomendado 3.10/3.12)**
   - Descargar desde https://www.python.org/downloads/windows/
   - Al instalar, **marcar la casilla** `Add Python to PATH` (muy importante).
2. **Git para Windows**
   - Descargar desde https://git-scm.com/download/win
   - Instalación con opciones por defecto.

Verificar que ambos quedaron instalados. Abrir **CMD o PowerShell**:

```bat
python --version
git --version
```

---

## 2. Configurar SSH (para clonar por SSH)

### 2.1 Generar la llave SSH (si no existe)

En **CMD o PowerShell**:

```bat
ssh-keygen -t ed25519 -C "tu-correo@correo.com"
```

Aceptar la ubicación por defecto (`C:\Users\TU_USUARIO\.ssh\id_ed25519`) y poner una frase de seguridad si se desea.

### 2.2 Copiar la llave pública

```bat
type C:\Users\TU_USUARIO\.ssh\id_ed25519.pub
```

Copiar el texto completo que imprime (empieza con `ssh-ed25519 AAAA...`).

### 2.3 Agregar la llave a GitHub

1. Ir a https://github.com/settings/keys
2. Click en **New SSH key**
3. En **Title** poner un nombre (ej: `Servidor Windows`)
4. Pegar la llave copiada y click en **Add SSH key**

### 2.4 Probar conexión SSH con GitHub

```bat
ssh -T git@github.com
```

Debe mostrar algo como:

```
Hi hgrestrepor! You've successfully authenticated, but GitHub does not provide shell access.
```

---

## 3. Clonar el repositorio

Con SSH (recomendado):

```bat
git clone git@github.com:hgrestrepor/cargue-masivo-contapymes.git
cd cargue-masivo-contapymes
```

Si se prefiere por HTTP:

```bat
git clone https://github.com/hgrestrepor/cargue-masivo-contapymes.git
cd cargue-masivo-contapymes
```

---

## 4. Instalar las dependencias

```bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Esto instala: `flask`, `bcrypt`, `pandas`, `openpyxl` y `requests`.

---

## 5. Iniciar el servidor

Desde la carpeta del proyecto:

```bat
python app.py
```

Al primer arranque la aplicación **crea automáticamente** la base de datos `users.db` con:

- **Usuario admin:** `adminceder`
- **Contraseña:** `AdminCeder345`

Verás en pantalla:

```
Servidor iniciado!
URL: http://localhost:5000
Admin: adminceder / AdminCeder345
```

---

## 6. Acceder a la aplicación

Abrir el navegador y entrar a:

```
http://localhost:5000
```

> Recomendación: no cerrar la ventana de CMD mientras la app esté corriendo.
> Si se cierra, volver a la carpeta del proyecto y ejecutar `python app.py` de nuevo.

### Credenciales de acceso

| Campo        | Valor           |
|--------------|-----------------|
| Usuario      | `adminceder`    |
| Contraseña   | `AdminCeder345` |

> **Importante:** cambia la contraseña o crea usuario administrador desde `http://localhost:5000/admin` antes de usarlo en producción.

---

## 7. Poner un alias `cargueceder:5000` en vez de `localhost:5000`

Para que la URL quede como `http://cargueceder:5000` en lugar de `http://localhost:5000`, se edita el archivo **hosts** de Windows.

### 7.1 Abrir el archivo hosts como Administrador

El archivo está en:

```
C:\Windows\System32\drivers\etc\hosts
```

Forma rápida de editarlo:

1. Abrir **Notepad** como administrador (click derecho sobre Bloc de notas → **Ejecutar como administrador**).
2. En Bloc de notas: **Archivo → Abrir**, pegar la ruta `C:\Windows\System32\drivers\etc\hosts`, y en "Tipo" seleccionar **Todos los archivos (*)**, abrir `hosts`.

### 7.2 Agregar la línea del alias

Al final del archivo agregar:

```
127.0.0.1       cargueceder
```

Guardar el archivo.

### 7.3 Verificar que el alias resuelva

En **CMD o PowerShell**:

```bat
ping cargueceder
```

Debe responder desde `127.0.0.1`.

### 7.4 Acceder por la nueva URL

Con el servidor corriendo (`python app.py`), abrir:

```
http://cargueceder:5000
```

También se puede ingresar a las páginas internas directamente:

```
http://cargueceder:5000/dashboard
http://cargueceder:5000/dashboard-transportes
http://cargueceder:5000/config-json
http://cargueceder:5000/registros
http://cargueceder:5000/admin
```

---

## 8. Carpetas y archivos importantes

| Archivo / Carpeta        | Descripción                                              |
|--------------------------|----------------------------------------------------------|
| `app.py`                 | Punto de entrada del servidor Flask                      |
| `procesador_excel.py`    | Lógica de mapeo de columnas y generación de JSONs        |
| `database.py`            | Base de datos SQLite (`users.db`)                        |
| `requirements.txt`       | Dependencias de Python                                   |
| `users.db`               | Base de datos (se crea sola en la primera ejecución)     |
| `jsons/`                 | JSONs generados al procesar los Excel                    |
| `templates/`             | Vistas HTML (dashboard, admin, etc.)                     |
| `uploads/`               | Excel subidos                                            |

---

## 9. Solución de problemas

### El comando `python` no se encuentra
- Reinstalar Python y marcar `Add Python to PATH`.
- O usar `py app.py` en vez de `python app.py`.

### El puerto 5000 está ocupado
```bat
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### `Permission denied (publickey)` al clonar por SSH
1. Confirmar que la llave pública se agregó en GitHub (sección 2.3).
2. Confirmar que `ssh -T git@github.com` autentica (sección 2.4).

### El alias `cargueceder` no resuelve
- Revisar `C:\Windows\System32\drivers\etc\hosts` y confirmar la línea `127.0.0.1 cargueceder`.
- Algunos antivirus/corporativos bloquean el archivo hosts; abrirlo como administrador.
- Probar `ipconfig /flushdns` después de editar.

---

## 10. Actualizar el proyecto después de cambios

Para traer los últimos cambios del repositorio:

```bat
git pull
```

Reiniciar el servidor (cerrar CMD y volver a `python app.py`).