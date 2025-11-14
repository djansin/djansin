<div dir="rtl" align="right" markdown="1" style="font-family: 'Vazirmatn RD', IRANSansX, Arial, sans-serif;">

# ☔️ [پِیْکَراژْهای](https://vn.amoosin.com/wiki/پیکراژ) (پیکربندی‌های) [اَهِمْناک](https://vn.amoosin.com/wiki/اهمناک) (مهم)

این [پِیْکَراژها](https://vn.amoosin.com/wiki/پیکراژ) (پیکربندی‌ها) نیز برای [عَمَلْدَن](https://vn.amoosin.com/wiki/عملدن) [دُرُساً](https://vn.amoosin.com/wiki/درسا) (کار کردن درست) یا [وُسِعْدَن](https://vn.amoosin.com/wiki/وسعدن) [ماهِرانِه](https://vn.amoosin.com/wiki/ماهرانه) (توسعه حرفه‌ای) پروژه [نیازْمائَنْد](https://vn.amoosin.com/wiki/نیازمائدن) (نیاز هستند)؛ که بشکل [وَضِحاء](https://vn.amoosin.com/wiki/وضحاء) (کامنت) - با [عَبِرات](https://vn.amoosin.com/wiki/عبرات) (عبارت) `Necessary` یا `Optional` - [عِیْنِشْدِه ئَنْد](https://vn.amoosin.com/wiki/عینشدن) (تعیین شده‌اند).

## 🐣 [پِیْکَراژْهای](https://vn.amoosin.com/wiki/پیکراژ) پایه

### 🌴 [کیاسْدَن](https://vn.amoosin.com/wiki/کیاسدن) [پِیْکِراءْهای](https://vn.amoosin.com/wiki/پیکراء) [وابَسْناک](https://vn.amoosin.com/wiki/وابَسْناک) به [اِجْرْلان](https://vn.amoosin.com/wiki/اجرلان) (هندل کردن پیکربندی‌های وابسته به محیط اجرا)

<div dir="ltr" align="left" markdown="1">

#### 📍 <span dir="ltr" markdown="1">`/config/settings/base.py`</span>

```python
# ...
SECRET_KEY = env.str("SECRET_KEY")
# ...
DEBUG = env.bool("DJANGO_DEBUG", False)
# ...
```

#### 📍 <span dir="ltr" markdown="1">`/envs/.env.api`</span>

```env
# ...
# This is an example of a secret key generated using base64 encoding.
# For production environments, it is recommended to use a randomly generated  secret key
# using a secure method such as:
# - openssl rand -base64 32 to generate a secure key using OpenSSL
# - python manage.py shell -c "from django.core.management.utils import  get_random_secret_key; print(get_random_secret_key())" function in Django to  generate a secure key
# - python -c "import secrets; print(secrets.token_urlsafe(32))" to generate a  secure random key
# - python -c "import base64, os; print(base64.urlsafe_b64encode(os.urandom(32))  decode('utf-8'))" to generate a key using base64 encoding
SECRET_KEY="django-insecure-x_%_+mqr0=r_3z-nv8d&y=qo^n^^@dv)m2=p!\$ya1v-z3_y^nf"

# Enable or disable Django debug mode. Set to True for development and debugging  purposes.
DJANGO_DEBUG=True
# ...
```

</div>

### 🌴 [تایِسْدَن](https://vn.amoosin.com/wiki/تایسدن) (سازماندهی کردن) فایل‌های ایستا (static)

<div dir="ltr" align="left" markdown="1">

#### 📍 <span dir="ltr" markdown="1">`/config/settings/base.py`</span>

```python
# ...
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# Static files settings
STATIC_URL = "static/"
# Directory where Django will collect static files (CSS, JS, images).
STATIC_ROOT = env.path("STATIC_ROOT")
# The directories where Django looks for static file sources.
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
# ...
```

#### 📍 <span dir="ltr" markdown="1">`/.env`</span>

```env
# ...
# The directory inside the container where Django stores collected static files (CSS, JS, images).
STATIC_ROOT="/assets/static"
# ...
```

#### 📍 <span dir="ltr" markdown="1">`/docker/nginx/configs/development/includes/django_static.conf`</span>

```nginx
# -------------------------------------------
# Primary static directory (non-collected, developer-editable static files)
# Served first when Django's app static sources exist
# -------------------------------------------
location /static/ {
    # First look in developer static sources
    alias /app/static/;

    # Prevent caching in development
    add_header Cache-Control "no-cache, no-store, must-revalidate";
    add_header Pragma "no-cache";
    add_header Expires 0;

    # Try loading the file; if not found, fallback to collected static files
    try_files $uri @fallback_static;
}

# -------------------------------------------
# Fallback static directory (collected static)
# Used when the developer static directory does not contain the file
# -------------------------------------------
location @fallback_static {
    # Rewrite the URL so /static/... becomes /<filename>
    rewrite ^/static/(.*)$ /$1 break;

    # Look for the file under /assets/static/<filename>
    root /assets/static;

    # If not found anywhere → return 404
    try_files $uri =404;
}
```

</div>

⚠️ برای [جَمِلْدَن](https://vn.amoosin.com/wiki/جملدن) (گردآوری کردن) فایل‌های ایستا این دستور را [بِاِجْر](https://vn.amoosin.com/wiki/اجریدن):

<div dir="ltr" align="left" markdown="1">

```bash
source ./yarsin collectstatic
```

</div>

### 🌴 [تایِسْدَن](https://vn.amoosin.com/wiki/تایسدن) (سازماندهی کردن) فایل‌های رسانه (media)

<div dir="ltr" align="left" markdown="1">

#### 📍 <span dir="ltr" markdown="1">`/config/settings/base.py`</span>

```python
# ...
# Media files settings
MEDIA_URL = "media/"
# Directory where Django will store user-uploaded media files.
MEDIA_ROOT = env.path("MEDIA_ROOT")
# ...
```

#### 📍 <span dir="ltr" markdown="1">`/.env`</span>

```env
# ...
# The directory inside the container where Django stores user-uploaded media files.
MEDIA_ROOT="/assets/media"
# ...
```

#### 📍 <span dir="ltr" markdown="1">`/docker/nginx/configs/development/includes/django_media.conf`</span>

```nginx
# -------------------------------------------
# Media files (user uploads, always served directly)
# -------------------------------------------
location /media/ {
    alias /assets/media/;

    # Disable caching in development (important for testing uploaded files)
    add_header Cache-Control "no-cache, no-store, must-revalidate";
    add_header Pragma "no-cache";
    add_header Expires 0;
}
```

</div>

### 🌴 [تایِسْدَن](https://vn.amoosin.com/wiki/تایسدن) (سازماندهی کردن) [زیرْبِرْکاها](https://vn.amoosin.com/wiki/زیربرکا) در پوشه `apps`

<div dir="ltr" align="left" markdown="1">

```bash
# This is the same as running "python manage.py startapp core"
source ./yarsin startapp core
```

#### 📍 <span dir="ltr" markdown="1">`/apps/core/apps.py`</span>

```python
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core" # The "name" was changed from "core" to "apps.core".
```

#### 📍 <span dir="ltr" markdown="1">`/config/settings/base.py`</span>

```python
# ...
# Application definition

INSTALLED_APPS = [
    # ...
    "apps.core",
]
# ...
```

</div>

### 🌴 [تایِسْدَن](https://vn.amoosin.com/wiki/تایسدن) (سازماندهی کردن) [وَضِعالْ‌ها](https://vn.amoosin.com/wiki/وضعال) در پوشه `templates`

<div dir="ltr" align="left" markdown="1">

#### 📍 <span dir="ltr" markdown="1">`/config/settings/base.py`</span>

```python
# ...
# ./config/settings/base.py
TEMPLATES = [
    {
        # ...
        "DIRS": [
            BASE_DIR / "templates",
        ],
        # ...
    },
]
# ...
```

</div>

</div>
