# Minimal settings for unit tests
SECRET_KEY = "16+af98faisj(6p2f*j(@sdiogjaef%t$+&m)nf@3494&q7_ty"
DEBUG = True
INSTALLED_APPS = ["django.contrib.auth", "django.contrib.contenttypes", "flippy"]
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
LANGUAGE_CODE = "en-us"
