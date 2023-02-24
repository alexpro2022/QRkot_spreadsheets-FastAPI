# Проект: QRkot_spreadsheets
Приложение для Благотворительного фонда поддержки котиков QRKot. 
Фонд собирает пожертвования на различные целевые проекты: на медицинское обслуживание нуждающихся хвостатых, на обустройство кошачьей колонии в подвале, на корм оставшимся без попечения кошкам — на любые цели, связанные с поддержкой кошачьей популяции.


## Оглавление
- [Технологии](#технологии)
- [Описание работы](#описание-работы)
- [Установка](#установка)
- [Запуск](#запуск)
- [Автор](#автор)


## Технологии
  - API - FastAPI, FastAPU Users, Pydantic, Uvicorn
  - Работа с реляционными БД - Alembic, SQLAlchemy
  - Dependency Injection
  - Google Drive, Google Sheets


[⬆️Оглавление](#оглавление)



## Описание работы
 - **Проекты:** 
В Фонде QRKot может быть открыто несколько целевых проектов. У каждого проекта есть название, описание и сумма, которую планируется собрать. После того, как нужная сумма собрана — проект закрывается.
Пожертвования в проекты поступают по принципу First In, First Out: все пожертвования идут в проект, открытый раньше других; когда этот проект набирает необходимую сумму и закрывается — пожертвования начинают поступать в следующий проект.

 - **Отчеты в Google таблицах:**
В приложении есть возможность формирования отчёта в гугл-таблице. В таблице представлены закрытые проекты, отсортированные по скорости сбора средств — от тех, что закрылись быстрее всего, до тех, что долго собирали нужную сумму. Также реализован функционал по управлению отчетами:
    * можно просмотреть все отчеты на Google диске
    * можно удалить определенный отчет с диска
    * можно полностью очистить диск - удаляются все отчеты с диска.

Все методы реализованы в базовом классе GoogleBaseClient в пакете google_package.

 - **Пожертвования:** 
Каждый пользователь может сделать пожертвование и сопроводить его комментарием. Пожертвования не целевые: они вносятся в фонд, а не в конкретный проект. Каждое полученное пожертвование автоматически добавляется в первый открытый проект, который ещё не набрал нужную сумму. Если пожертвование больше нужной суммы или же в Фонде нет открытых проектов — оставшиеся деньги ждут открытия следующего проекта. При создании нового проекта все неинвестированные пожертвования автоматически вкладываются в новый проект.

 - **Пользователи:** 
Целевые проекты создаются администраторами сайта.
Зарегистрированные пользователи могут отправлять пожертвования и просматривать список своих пожертвований.
Любой пользователь может видеть список всех проектов, включая требуемые и уже внесенные суммы. Это касается всех проектов — и открытых, и закрытых.

[⬆️Оглавление](#оглавление)



## Установка:
1. Клонировать репозиторий с GitHub:
```
git@github.com:alexpro2022/QRkot_spreadsheets.git
```

2. Перейти в созданную директорию проекта:
```
cd QRkot_spreadsheets.git
```

3. Создать и активировать виртуальное окружение:
```
python -m venv venv
```
* Если у вас Linux/macOS

    ```
    source venv/bin/activate
    ```

* Если у вас windows

    ```
    source venv/Scripts/activate
    ```

4. Установить в виртуальное окружение все необходимые зависимости из файла **requirements.txt**:
```
python -m pip install --upgrade pip
pip install -r requirements.txt
pip list
```

5. В корневой директории **/QRkot_spreadsheets** создать файл **.env** и заполнить его переменными окружения (пример заполнения можно посмотреть в файле **env_example** - можно переименовать этот файл в .env и присвоить кастомные значения существующим переменным). При необходимости добавить требуемые переменные окружения в файл **.env** и в файл конфигурации **app/core/config.py**

6. В проекте уже инициализирована система миграций Alembic с настроенной автогенерацией имен внешних ключей моделей и создан файл первой миграции. Чтобы ее применить, необходимо выполнить команду:
```
(venv) ...$ alembic upgrade head
```
Будут созданы все таблицы из файла миграций.

[⬆️Оглавление](#оглавление)



## Запуск:
Из корневой директории проекта выполните команду:

```
(venv) $  uvicorn app.main:app
```
Сервер uvicorn запустит приложение по адресу http://127.0.0.1:8000.
При первом запуске будет создан суперюзер (пользователь с правами админа) с параметрами указанными в переменных окружения FIRST_SUPERUSER_EMAIL и FIRST_SUPERUSER_PASSWORD в .env-файле.

[⬆️Оглавление](#оглавление)



## Применение:
Администрирование приложения может быть осуществлено через Swagger доступный по адресу http://127.0.0.1:8000/docs.
Это приложение позволяет осуществлять http-запросы к работающему сервису, тем самым можно управлять проектами, пожертвованиями и пользователями в рамках политики сервиса (указано в Swagger для каждого запроса). 
Для доступа к этим функциям необходимо авторизоваться в Swagger, используя credentials из .env файла:

    1. Нажмите:
        * на символ замка в строке любого эндпоинта или 
        * на кнопку Authorize в верхней части Swagger. 
    Появится окно для ввода логина и пароля.

    2. Введите credentials в поля формы: 
        * в поле username — значение переменной окружения FIRST_SUPERUSER_EMAIL, 
        * в поле password — значение переменной окружения FIRST_SUPERUSER_PASSWORD. 
    В выпадающем списке Client credentials location оставьте значение Authorization header, 
    остальные два поля оставьте пустыми; нажмите кнопку Authorize. 
Если данные были введены правильно, и таблица в БД существует — появится окно с подтверждением авторизации, нажмите Close. 
Чтобы разлогиниться — перезагрузите страницу.



## Автор
[Aleksei Proskuriakov](https://github.com/alexpro2022)

[⬆️В начало](#Проект-QRkot_spreadseets)