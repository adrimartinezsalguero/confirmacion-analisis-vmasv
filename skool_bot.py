import os
import time
import logging
import schedule
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# ─────────────────────────────────────────────
#  CONFIGURACIÓN — edita solo esta sección
# ─────────────────────────────────────────────

SKOOL_EMAIL    = os.environ.get("SKOOL_EMAIL", "TU_EMAIL@gmail.com")
SKOOL_PASSWORD = os.environ.get("SKOOL_PASSWORD", "TU_PASSWORD")
SKOOL_GROUP_URL = os.environ.get("SKOOL_GROUP_URL", "https://www.skool.com/TU-GRUPO/feed")

# Palabras clave que identifican el post (título O categoría)
POST_KEYWORDS = ["análisis", "sesión de análisis", "análisis de llamadas", "reserva tu sitio"]

# Etiqueta/categoría del post (déjala vacía "" si no aplica)
POST_CATEGORY = "análisis de llamadas"

# Los 3 comentarios que quieres publicar (en orden)
COMMENTS = [
    "Comentario 1: escribe aquí tu primer texto exacto.",
    "Comentario 2: escribe aquí tu segundo texto exacto.",
    "Comentario 3: escribe aquí tu tercer texto exacto.",
]

# Segundos entre cada comentario (para no parecer bot)
DELAY_BETWEEN_COMMENTS = 8

# ─────────────────────────────────────────────
#  LOGGING
# ─────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger(__name__)

# ─────────────────────────────────────────────
#  LÓGICA PRINCIPAL
# ─────────────────────────────────────────────

def post_matches(post_element) -> bool:
    """Devuelve True si el post contiene alguna keyword o la categoría correcta."""
    try:
        text = post_element.inner_text().lower()
        # Comprobar keywords en el texto del post
        for kw in POST_KEYWORDS:
            if kw.lower() in text:
                return True
        # Comprobar categoría
        if POST_CATEGORY and POST_CATEGORY.lower() in text:
            return True
    except Exception:
        pass
    return False


def already_commented(post_element, email: str) -> bool:
    """Comprueba si ya hemos comentado en este post para evitar duplicados."""
    try:
        comments_text = post_element.inner_text().lower()
        # Usamos el primer comentario como firma de que ya actuamos
        if COMMENTS[0][:30].lower() in comments_text:
            log.info("Post ya comentado anteriormente — omitiendo.")
            return True
    except Exception:
        pass
    return False


def publish_comments(page, post_element) -> bool:
    """Hace clic en el post y publica los 3 comentarios."""
    try:
        # Abrir el post individual
        link = post_element.query_selector("a[href*='/p/']")
        if not link:
            log.warning("No se encontró enlace al post individual.")
            return False

        post_url = link.get_attribute("href")
        if not post_url.startswith("http"):
            post_url = "https://www.skool.com" + post_url

        log.info(f"Abriendo post: {post_url}")
        page.goto(post_url, wait_until="networkidle", timeout=30000)
        time.sleep(3)

        for i, comment_text in enumerate(COMMENTS, start=1):
            log.info(f"Publicando comentario {i}/{len(COMMENTS)}...")

            # Buscar el campo de comentario
            comment_box = page.locator(
                "div[contenteditable='true'], textarea[placeholder*='comment'], "
                "div[data-placeholder*='comment'], div[role='textbox']"
            ).last

            comment_box.click()
            time.sleep(1)
            comment_box.fill("")
            comment_box.type(comment_text, delay=30)
            time.sleep(1)

            # Buscar botón de enviar
            send_btn = page.locator(
                "button:has-text('Post'), button:has-text('Comment'), "
                "button:has-text('Send'), button[type='submit']"
            ).last
            send_btn.click()

            log.info(f"✅ Comentario {i} publicado.")
            if i < len(COMMENTS):
                log.info(f"Esperando {DELAY_BETWEEN_COMMENTS}s antes del siguiente...")
                time.sleep(DELAY_BETWEEN_COMMENTS)

        return True

    except PlaywrightTimeout:
        log.error("Timeout al intentar publicar comentarios.")
        return False
    except Exception as e:
        log.error(f"Error al publicar comentarios: {e}")
        return False


def run_bot():
    log.info("=" * 50)
    log.info(f"🤖 Bot iniciado — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info("=" * 50)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        try:
            # ── LOGIN ──────────────────────────────────────
            log.info("Iniciando sesión en Skool...")
            page.goto("https://www.skool.com/login", wait_until="networkidle", timeout=30000)
            time.sleep(2)

            page.locator("input[type='email'], input[name='email']").fill(SKOOL_EMAIL)
            page.locator("input[type='password'], input[name='password']").fill(SKOOL_PASSWORD)
            page.locator("button[type='submit'], button:has-text('Sign in'), button:has-text('Log in')").click()

            page.wait_for_url(lambda url: "login" not in url, timeout=15000)
            log.info("✅ Login exitoso.")
            time.sleep(3)

            # ── MONITOREO DEL FEED ─────────────────────────
            log.info(f"Accediendo al feed: {SKOOL_GROUP_URL}")
            page.goto(SKOOL_GROUP_URL, wait_until="networkidle", timeout=30000)
            time.sleep(3)

            # Escanear hasta 3 veces (el post puede tardar unos minutos en aparecer)
            max_scans = 3
            found = False

            for scan in range(1, max_scans + 1):
                log.info(f"Escaneo {scan}/{max_scans} del feed...")

                # Recargar para ver posts nuevos
                if scan > 1:
                    page.reload(wait_until="networkidle")
                    time.sleep(3)

                posts = page.locator("div[data-testid='post'], div[class*='post'], article").all()
                log.info(f"Posts encontrados en pantalla: {len(posts)}")

                for post in posts:
                    if post_matches(post):
                        if already_commented(post, SKOOL_EMAIL):
                            found = True
                            break
                        log.info("🎯 Post de análisis detectado. Publicando comentarios...")
                        success = publish_comments(page, post)
                        if success:
                            log.info("🎉 Los 3 comentarios fueron publicados con éxito.")
                        found = True
                        break

                if found:
                    break

                if scan < max_scans:
                    log.info("Post no encontrado aún. Esperando 3 minutos antes del siguiente escaneo...")
                    time.sleep(180)

            if not found:
                log.warning("⚠️ No se encontró el post de análisis en esta ejecución.")

        except Exception as e:
            log.error(f"Error general en el bot: {e}")
        finally:
            browser.close()
            log.info("Navegador cerrado.")


# ─────────────────────────────────────────────
#  SCHEDULER — corre cada viernes a las 19:00
# ─────────────────────────────────────────────

def main():
    log.info("Scheduler activo. El bot correrá cada viernes a las 19:00 (hora España).")
    schedule.every().friday.at("19:00").do(run_bot)

    # Para probar sin esperar al viernes, descomenta la línea siguiente:
    # run_bot()

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
