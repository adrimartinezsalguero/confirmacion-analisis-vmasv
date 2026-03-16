# 🤖 Guía de Despliegue — Skool Auto-Comment Bot
## De cero a funcionando en ~20 minutos

---

## ¿Qué hace este bot?
Cada viernes a las 19:00 (hora España), el bot:
1. Entra automáticamente a tu cuenta de Skool
2. Escanea el feed del grupo buscando el post de análisis de llamadas
3. Si lo encuentra, publica tus 3 comentarios con un intervalo natural entre ellos
4. Si el post tarda en aparecer, reintenta cada 3 minutos hasta 3 veces

---

## PASO 1 — Editar el script con tus datos

Abre `skool_bot.py` y edita la sección de configuración:

```python
SKOOL_EMAIL    = "tu_email@gmail.com"
SKOOL_PASSWORD = "tu_contraseña"
SKOOL_GROUP_URL = "https://www.skool.com/nombre-de-tu-grupo/feed"

POST_KEYWORDS = ["análisis", "sesión de análisis", "reserva tu sitio"]
POST_CATEGORY = "análisis de llamadas"   # la etiqueta exacta del post

COMMENTS = [
    "Tu primer comentario exacto aquí.",
    "Tu segundo comentario exacto aquí.",
    "Tu tercer comentario exacto aquí.",
]
```

⚠️ Las credenciales las pondrás como variables de entorno en Railway (más seguro).
En el script déjalas con os.environ.get() tal como están.

---

## PASO 2 — Crear cuenta en GitHub (si no tienes)

1. Ve a https://github.com
2. Crea una cuenta gratuita
3. Crea un repositorio nuevo llamado `skool-bot` (privado ✅)
4. Sube los 3 archivos: `skool_bot.py`, `requirements.txt`, `Dockerfile`

### Cómo subir los archivos (sin saber Git):
1. En tu repositorio GitHub, haz clic en **"Add file" → "Upload files"**
2. Arrastra los 3 archivos
3. Clic en **"Commit changes"**

---

## PASO 3 — Desplegar en Railway (servidor gratuito)

Railway tiene un plan gratuito de ~500 horas/mes — más que suficiente.

1. Ve a https://railway.app
2. Regístrate con tu cuenta de GitHub
3. Clic en **"New Project"**
4. Selecciona **"Deploy from GitHub repo"**
5. Elige tu repositorio `skool-bot`
6. Railway detectará el Dockerfile automáticamente ✅

---

## PASO 4 — Configurar variables de entorno en Railway

En Railway, ve a tu proyecto → **"Variables"** → añade:

| Variable         | Valor                                          |
|-----------------|------------------------------------------------|
| SKOOL_EMAIL     | tu_email@gmail.com                             |
| SKOOL_PASSWORD  | tu_contraseña_de_skool                         |
| SKOOL_GROUP_URL | https://www.skool.com/nombre-tu-grupo/feed     |
| TZ              | Europe/Madrid                                  |

⚠️ La variable TZ es importante para que las 19:00 sean hora España.

---

## PASO 5 — Desplegar y verificar

1. Clic en **"Deploy"**
2. Verás los logs en tiempo real
3. Deberías ver: `Scheduler activo. El bot correrá cada viernes a las 19:00`

✅ Ya está funcionando. No necesitas hacer nada más.

---

## PASO 6 — Probar sin esperar al viernes

Para verificar que funciona antes del viernes:

1. En `skool_bot.py`, busca esta línea y quítale el `#`:
```python
# run_bot()
```
2. Súbela a GitHub de nuevo
3. Railway redesplegará y ejecutará el bot una vez inmediatamente
4. Revisa los logs para ver si hace login y encuentra posts

Cuando confirmes que funciona, vuelve a poner el `#` y redespliega.

---

## RESOLUCIÓN DE PROBLEMAS

**"No se encontró el post de análisis"**
→ Las keywords no coinciden con el texto real del post.
→ Abre el post manualmente, copia el título exacto y añádelo a POST_KEYWORDS.

**"Error en login"**
→ Verifica las variables de entorno en Railway.
→ Skool puede tener captcha. Si ocurre, escríbeme.

**"Timeout al publicar comentarios"**
→ El selector del campo de comentario cambió.
→ Es lo más común cuando Skool actualiza su web. Avísame y lo actualizo.

---

## Estructura de archivos

```
skool-bot/
├── skool_bot.py      ← Script principal
├── requirements.txt  ← Dependencias Python
├── Dockerfile        ← Configuración del servidor
└── GUIA.md          ← Esta guía
```

---

## Coste total: 0€/mes 🎉
- GitHub: gratuito
- Railway: gratuito (500h/mes, el bot usa ~1h/semana = ~4h/mes)
