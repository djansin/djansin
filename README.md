<div dir="rtl" align="right" markdown="1" style="font-family: 'Vazirmatn RD', IRANSansX, Arial, sans-serif;">

# 🪵 جَنْسین

«**جَنْسین**» [یه](https://vn.amoosin.com/wiki/یه) پروژه [شَمِلاء](https://vn.amoosin.com/wiki/شملاء) (شامل) یک سیستم [چَنْخَدِماءی](https://vn.amoosin.com/wiki/جندخدماءی) (چند سرویسی) برپایه Docker [ئَد](https://vn.amoosin.com/wiki/ئدن) (است) که برای [وُسِعْدن](https://vn.amoosin.com/wiki/وسعدن) (توسعه دادن) و [اِجْریدَن](https://vn.amoosin.com/wiki/اجریدن) (اجرا کردن) برنامه‌ها برپایه Django [طَرْحِشْدِه](https://vn.amoosin.com/wiki/طرحشدن) (طراحی شده است).

---

## 🚀 [کُلْبین](https://vn.amoosin.com/wiki/کلبین) (دید کلی)

این پروژه از چهار [خَدِماء](https://vn.amoosin.com/wiki/خدماء) (سرویس) اصلی [شَکِلِشْدِه ئَد](https://vn.amoosin.com/wiki/شکلشدن) (تشکیل شده است):

1. web (Nginx): برای [هُدیدَن](https://vn.amoosin.com/wiki/هدیدن) [عُبورِشاء](https://vn.amoosin.com/wiki/عبورشاء) (ترافیک) HTTP به [خَدِماءْها](https://vn.amoosin.com/wiki/خدماء) (سرویس‌ها):
2. api (Django): چارچوب جنگو که هسته اصلی برنامه [ئَد](https://vn.amoosin.com/wiki/ئدن) (است)؛
3. db (PostgreSQL): پایگاه‌داده اصلی پروژه؛
4. pgadmin (pgAdmin4): ابزاری تحت وب برای [اِدارْدَن](https://vn.amoosin.com/wiki/اداردن) (مدیریت کردن) پایگاه‌داده اصلی.

![تهبین](./docs/assets/جنگو.png)

و [یه](https://vn.amoosin.com/wiki/یه) دستیار به نام `yarsin` برای [تایِسْدَن](https://vn.amoosin.com/wiki/تایسدن) (سازماندهی کردن) دستورها و فایل‌های `bash`؛ بطوریکه برای [سازْدَن](https://vn.amoosin.com/wiki/سازدن) (ساختن) [ریزبرکاهای](https://vn.amoosin.com/wiki/ریزبرکا) (app) `core`، `user`، و `user_profile` [کایَد](https://vn.amoosin.com/wiki/کاید) (کافیه) دستور زیر را [باِجْری](https://vn.amoosin.com/wiki/اجریدن) (اجرا کنی):

<div dir="ltr" align="left" markdown="1">

```bash
source ./yarsin startapp core user user_profile
```

</div>

![یارسین](./docs/assets/یارسین.png)

و برای [مانوزدن](https://vn.amoosin.com/wiki/مانوزدن) (بکاپ گرفتن از) پایگاه‌داده‌ها:

<div dir="ltr" align="left" markdown="1">

```bash
source ./yarsin backup data
```

</div>

![مانوزدن](./docs/assets/مانوزدن.png)

و برای [اِضافْدَن](https://vn.amoosin.com/wiki/اضافدن) [یه](https://vn.amoosin.com/wiki/یه) فایل script، [کایَد](https://vn.amoosin.com/wiki/کاید) آن را در <span dir="ltr" markdown="1">`./scripts/sources`</span> [بِمَحِلی](https://vn.amoosin.com/wiki/مَحِلْدَن) (قرار بدهی):

<div dir="ltr" align="left" markdown="1">

```bash
# ./scripts/sources/test
#!/usr/bin/env bash

echo "This is a test bash script..."
```

</div>

سپس با <span dir="ltr" markdown="1">`source ./yarsin <script name>`</span> [بِاِجْری](https://vn.amoosin.com/wiki/اجریدن) [اَش](https://vn.amoosin.com/wiki/اش) (اجرایش کنی):

<div dir="ltr" align="left" markdown="1">

```bash
source ./yarsin test
```

</div>

---

## 🏄‍♂️ [بَهِرِش](https://vn.amoosin.com/wiki/بهرش) (روش استفاده)

برای [بِهِرْدَن](https://vn.amoosin.com/wiki/بهردن) (استفاده کردن از) این پروژه [باید](https://vn.amoosin.com/wiki/باید) [داکر](https://docs.docker.com/desktop/) و [داکرکامپوز](https://docs.docker.com/compose/install/) در سیستم [اَت](https://vn.amoosin.com/wiki/ات) (تو) [نَصْبِشدِه بِئَنْد](https://vn.amoosin.com/wiki/نصبشتن) (نصب شده باشند). و [هایَد](https://vn.amoosin.com/wiki/هاید) (بهتره) [Makefile](https://makefiletutorial.com/) هم [بِدارائی](https://vn.amoosin.com/wiki/دارائدن) (داشته باشی) وگرنه باید دستورهای در `Makefile` را بشکل دستی [بِاِجْری](https://vn.amoosin.com/wiki/اجریدن) (اجرا کنی).

### ⛳️ [عَلَنْدَن](https://vn.amoosin.com/wiki/علندن) [نیازْماءْها](https://vn.amoosin.com/wiki/نیازماء)

برای [عَلَنْدَن](https://vn.amoosin.com/wiki/علندن) [تَنیازْماءهای](https://vn.amoosin.com/wiki/نیازماء) (نیازمندی‌های) هر [اِجْرْلان](https://vn.amoosin.com/wiki/اجرلان) (محیط اجرا؛ Environment) [تایَد](https://vn.amoosin.com/wiki/تاید) (می‌توانی) فایل [مُنِسْناک](https://vn.amoosin.com/wiki/منسناک) (مناسب) را [بِبَهْری](https://vn.amoosin.com/wiki/بهردن) (استفاده کنی):

<div dir="ltr" align="left" markdown="1">

#### 📍 <span dir="ltr" markdown="1">`/requirements/base.txt`</span>

```requirement
## Building Powerful Web Applications with Django and Environment Variable Management
Django==5.2.8                           # Core Python web framework used to build scalable, secure, and maintainable applications.
django-environ==0.12.0                  # Environment variable management for secure and flexible configuration handling.

daphne==4.2.1                           # ASGI server that enables Django Channels to support asynchronous requests and WebSockets.
channels==4.3.1                         # Framework for handling WebSockets and asynchronous features in Django.
```

#### 📍 <span dir="ltr" markdown="1">`/requirements/development.txt`</span>

```requirement
-r base.txt

## Database Connectivity
psycopg2-binary==2.9.11                 # PostgreSQL adapter for Python that provides efficient database communication.

## Code Quality and Formatting Tools
isort==5.13.2                           # Tool that automatically organizes and orders Python imports.
flake8==7.0.0                           # Linting tool for enforcing Python code style and detecting common issues.
Flake8-pyproject==1.2.3                 # Flake8 extension that allows configuration through pyproject.toml.
black==24.3.0                           # Opinionated code formatter for maintaining consistent code style across the project.

colorlog==6.10.1                        # Enhances logging output with colors to improve readability during development.

pytest-django==4.11.1                   # Pytest plugin that provides Django integration for simplified and powerful testing workflows.
```

</div>

⚠️ برای [وارْدَن](https://vn.amoosin.com/wiki/واردن) (تبدیل کردن) [نَشِرْناسْ‌های](https://vn.amoosin.com/wiki/نشرناس) (شماره نسخه‌های) بسته‌های [عَلَنِشْدِه](https://vn.amoosin.com/wiki/علنشدن) (اعلان شده) در فایل‌های <span dir="ltr">`./requirements/*.txt`</span> به آخرین [نِشِرْماء](https://vn.amoosin.com/wiki/نشرماء) (نسخه؛ ورژن) پایدار، [تایَد](https://vn.amoosin.com/wiki/تاید) (می‌توانی) دستور زیر را [بِاِجْری](https://vn.amoosin.com/wiki/اجریدن) (اجرا کنی):

<div dir="ltr" align="left" markdown="1">

```bash
make update-requires # OR: python ./scripts/update_requirements.py
```

</div>

### ⛳️ [آغازْدَن](https://vn.amoosin.com/wiki/آغازدن) پروژه

[پَسَز](https://vn.amoosin.com/wiki/پسز) [عَلَنْدَن](https://vn.amoosin.com/wiki/علندن) (اعلان کردن) [نیازْماء‌های](https://vn.amoosin.com/wiki/نیازماء) پروژه [اَت](https://vn.amoosin.com/wiki/ات)، دستور زیر را [بِاِجْر](https://vn.amoosin.com/wiki/اجریدن) (اجرا کن) تا [یه](https://vn.amoosin.com/wiki/یه) پروژه جدید جنگو برایت [ایجِشَد](https://vn.amoosin.com/wiki/ایجشدن) (ایجاد شود):

<div dir="ltr" align="left" markdown="1">

```bash
# This is the same as running "django-admin startproject config ."
make init # OR: source ./yarsin init
```

</div>

### ⛳️ [پِیْکَرْدَن](https://vn.amoosin.com/wiki/پیکریدن) جنگو

چون فایل [پِیْکَراء](https://vn.amoosin.com/wiki/پیکراء) (پیکربندی) <span dir="ltr" markdown="1">`./config/settings.py`</span> به <span dir="ltr" markdown="1">`./config/settings/base.py`</span> [نَقْلِشْدِه](https://vn.amoosin.com/wiki/نقلشدن) (منتقل شده)، [پِیْکَراف](https://vn.amoosin.com/wiki/پیکراف) (عالم پیکربندی) `BASE_DIR` را [بِصَلِح](https://vn.amoosin.com/wiki/صلحدن) (اصلاح کن):

<div dir="ltr" align="left" markdown="1">

#### 📍 <span dir="ltr" markdown="1">`/config/settings/base.py`</span>

```python
# ...
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# ...
```

</div>

و از [غَیِرْپَذیرهای](https://vn.amoosin.com/wiki/غیرپذیر) [مَحِلْناک](https://vn.amoosin.com/wiki/محلناک) (متغیرهای محلی) برای [عِیْنْدَن](https://vn.amoosin.com/wiki/عیندن) (اعلان کردن) `DEBUG` و `DEBUG` [بِبَهْر](https://vn.amoosin.com/wiki/بهردن) (استفاده کن):

<div dir="ltr" align="left" markdown="1">

#### 📍 <span dir="ltr" markdown="1">`/config/settings/base.py`</span>

```python
# ...
from environ import Env

env = Env()
# ...
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DJANGO_DEBUG", False)
# ...
```

</div>

و <span dir="ltr" markdown="1">`ALLOWED_HOSTS = []`</span> را برای [حَفِظْدَن](https://vn.amoosin.com/wiki/حفظدن) [اَمَنیَّت](https://vn.amoosin.com/wiki/امنیت) از <span dir="ltr" markdown="1">`./config/settings/base.py`</span> به <span dir="ltr" markdown="1">`./config/settings/development.py`</span> [بِنَقِل](https://vn.amoosin.com/wiki/نقلدن):

<div dir="ltr" align="left" markdown="1">

#### 📍 <span dir="ltr" markdown="1">`/config/settings/development.py`</span>

```python
# ...
# List of host/domain names that this Django site can serve. Must be set in production to prevent host header attacks.
ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:9000',
    'http://127.0.0.1:9000',
]
```

</div>

### ⛳️ [پِیْکَرْدَن](https://vn.amoosin.com/wiki/پیکریدن) پایگاه‌داده

برای [پِیْکَرْدَن](https://vn.amoosin.com/wiki/پیکردن) (پیکربندی) جنگو بِقَصْد [بَهِرْدَن](https://vn.amoosin.com/wiki/بهردن) (استفاده کردن از) پایگاه‌داده `PostgreSQL`، [پِیْکَراف](https://vn.amoosin.com/wiki/پیکراف) `DATABASES` را [بِصَلِح](https://vn.amoosin.com/wiki/صلحدن):

<div dir="ltr" align="left" markdown="1">

#### 📍 <span dir="ltr" markdown="1">`/config/settings/base.py`</span>

```python
# ...
DATABASES = {"default": env.db("DATABASE_URL")}
# ...
```

</div>

### ⛳️ [پِیْکَرْدَن](https://vn.amoosin.com/wiki/پیکریدن) فایل‌های ایستا

 برای [عَلَنْدَن](https://vn.amoosin.com/wiki/علندن) محل [جَمِلْدَن](https://vn.amoosin.com/wiki/جملدن) (گرآوری) فایل‌های ایستا، با [غَیْمَل](https://vn.amoosin.com/wiki/غیمل) (متغیر محلی) `STATIC_ROOT` پوشه [جَمِلاژ](https://vn.amoosin.com/wiki/جملاژ) (گردآوری) فایل‌های ایستا را [بِعَلِم](https://vn.amoosin.com/wiki/علمدن) (اعلام کن):

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

</div>

سپس [مَحِلاف](https://vn.amoosin.com/wiki/محلاف) (مسیر) ریشه فایل‌های ایستا را در Nginx [بِعَلِم](https://vn.amoosin.com/wiki/علمدن) (اعلام کن):

<div dir="ltr" align="left" markdown="1">

</div>

🪜 [پِیْکَراژ‌ْهای (پیکربندی‌های) اَهِمْناک (مهم) دیگر...](docs/after_installing.md)

### ⛳️ [اِجْریدَن](https://vn.amoosin.com/wiki/اجریدن) پروژه

درپایان، برای [اِجْریدَن](https://vn.amoosin.com/wiki/اجریدن) (به اجرا درآوردن) پروژه‌ات دستور زیر را [بِاِجْرْ](https://vn.amoosin.com/wiki/اجریدن) (اجرا کن):

<div dir="ltr" align="left" markdown="1">

```bash
make up # OR: docker compose up -d

# To fix the permission issue, run the following command:
source ./yarsin init-volumes

# To view the Django server logs, run the following command:
docker logs djansin_api
```

</div>

پایان! 🎉 حالا ازطریق [وَنْداءْهای](https://vn.amoosin.com/wiki/ونداء) (لینک‌های) زیر [توانائی](https://vn.amoosin.com/wiki/توانائدن) (می‌توانی) به هر یک از [خَدِماءها](https://vn.amoosin.com/wiki/خدماء) [اَت](https://vn.amoosin.com/wiki/ات) (سرویس‌هایت) [بِدَسِسی](https://vn.amoosin.com/wiki/دسسدن) (دسترسی بیابی):

- پروژه (صفحه جنگو): <span dir="ltr">[localhost:9000/](http://localhost:9000/)</span>
- [اِدارال](https://vn.amoosin.com/wiki/ادارال) پایگاه‌داده (pgAdmin): <span dir="ltr">[pg.localhost:9000/](http://pg.localhost:9000/)</span> (user: `admin@email.com`, pass: `123456`)

---

## 🪄 یارْسین

برای [اِجْریدَن](https://vn.amoosin.com/wiki/اجریدن) (اجرا کردن) دستورهای `django-admin` [تَوانائی](https://vn.amoosin.com/wiki/تونائدن) (می‌توانی) دستیار <span dir="ltr">`./yarsin`</span> را مانند زیر [بِبَهِری](https://vn.amoosin.com/wiki/بهردن) (به‌کار بگیری):

<div dir="ltr" align="left" markdown="1">

```bash
source ./yarsin [django-admin comments|cuatom camments] [options]
```

</div>

مثلا، برای [آغازْدَن](https://vn.amoosin.com/wiki/آغازدن) (آغاز کردن) چند [ریزبرکا](https://vn.amoosin.com/wiki/ریزبرکا) (برنامه کاربردی) [کایَد](https://vn.amoosin.com/wiki/کاید) (کافیه) مانند زیر [بِعَمَلی](https://vn.amoosin.com/wiki/عملیدن) (عمل کنی):

<div dir="ltr" align="left" markdown="1">

```bash
source ./yarsin startapp core user
```

</div>

⚠️ این درمورد همه دستورهای [عَبِرْناک](https://vn.amoosin.com/wiki/عبرناک) (معتبر) `django-admin` [قَرِرْمائَد](https://vn.amoosin.com/wiki/قررمائدن) (برقرار است)!

### 🩺 دستورهای [نِگَهِش](https://vn.amoosin.com/wiki/نگهش) (نگهداری)

- [مانوزْدَن](https://vn.amoosin.com/wiki/مانوزدن) [سَمْپاد](https://vn.amoosin.com/wiki/سمپاد) (بکاپگیری در سطح فایل):

  <div dir="ltr" align="left" markdown="1">

  ```bash
  source ./yarsin backup dbms
  ```

  </div>

- [مانوزْدَن](https://vn.amoosin.com/wiki/مانوزدن) پایگاه‌داده (بکاپگیری در سطح پایگاه‌داده):

  <div dir="ltr" align="left" markdown="1">

  ```bash
  source ./yarsin backup data
  ```

  </div>

- [پیشارْدَن](https://vn.amoosin.com/wiki/پیشاردن) (برگرداندن) [سمپاد](https://vn.amoosin.com/wiki/سمپاد):

  <div dir="ltr" align="left" markdown="1">

  ```bash
  source ./yarsin restore dbms
  ```

  </div>

- [پیشارْدَن](https://vn.amoosin.com/wiki/پیشاردن) (برگرداندن) پایگاه‌داده:

  <div dir="ltr" align="left" markdown="1">

  ```bash
  source ./yarsin restore data
  ```

  </div>

---

## 💡 چگونه

- [چگونه ریزبِرْکاها را در یک پوشه بِتایِسیم (سازماندهی کنیم)؟](docs/using_an_apps_folder.md)
- [چگونه فایل‌های ایستا و رسانه را بِتایِسیم (سازماندهی کنیم)؟](docs/handling_django_static_and_media_files.md)
- [چگونه پروژه اِمان را بِمِلّیکیم (ملی‌ساز) و بِمِلَلِکیم (بین‌المللی‌سازی کنیم)؟](docs/internationalization_and_iocalization.md)
- [چگونه اِطَلِعان‌های آسیباوَر (اطلاعات حساس) را با غَیِرْپَذیر مَحِلْناک (متغیرهای محلی) بِکیاسیم (هندل کنیم)؟](docs/using_env_file_in_django.md)

</div>
