# RC_WH

программа разработана для учета активов IT на складах компании
### она позволяет:
- вести учет активов на складах
- следить за перемещениями активов
- ремонтировать и списаывать активы
- отслеживать ремонты активов

### Бекенд написан на пайтон и включает в себя 2 части:
- бот для телеграма
- приложение на fastapi (доступ по адресу http://{адрес сервера}:9000/docs)
#### эти две части программы связаны через базу данных SQLite
#### работа с базой данных реализована с использованием библиотеки sqlalchemy
#### для телеграмма используется библиотека aiogram
#### для шаблонизации данных на фронтенд используется jinja2
### Фронтенд написан на JS с ипользованием JQuery

---------------------------
# **WEB TERMINAL (http://{адрес сервера}/app:9000)**:
## АВТОРИЗАЦИЯ И ДОСТУПЫ

управление активами реализовано на основе разделения пользователей на админов и юзеров
это реализовано через выдачу токена JWT, в который передается ID и login пользователя
---- 
токен действует 1 час
программа раз в 5 секунд проверяет валидность jwt токена и после истечения срока действия - пользователя выкинет обратно на авторизацию
----
админы имеют все права для работы с активами и пользователями
- создавать и удалять пользователей
- создавать и удалять активы

пользоатели могут:
- менять описание любого актива
- удалять свои активы

# ЛОГИКА
## Если актив в ремонте (статус - ремонт)
(реализация на беке)
- удаление - нет
- перемещение - нет
- изменение описания - да (сделать надо что бы нет)
- взять в ремонт - нет
- быстрый ремонт - нет
- выдать с ремонта - да
- добавить файлы - да
- добавить описание ремонта - да
- отправить на списание - да
------------------------
** ремонт это перемещение
** быстрый ремонт это не перемещение

## Если актив отправлен на списание (статус - списание)
(реализация на фронте)
- удаление - нет 
- перемещение - нет
- изменение описания - нет
- взять в ремонт - нет
- быстрый ремонт - нет
- выдать с ремонта - нет
- добавить файлы - нет
- добавить описание ремонта - нет
- отправить на списание - нет
-- списать в архив из таблицы списания - да
___________________________________
** списание это перемещение
отправка на утилизацию это не перемещение. при утилизации все данные об активах из таблицы списания перемещаются в таблицу 
архивации



## Если актив выдан (статус - выдан)
- удаление - да
- перемещение - да
- изменение описания - да
- взять в ремонт - да
- быстрый ремонт - да
- выдать с ремонта - нет
- добавить файлы - да
- добавить описание ремонта - нет
- отправить на списание - да

## Если актив на хранении (статус - хранение)
- удаление - да
- перемещение - да
- изменение описания - да
- взять в ремонт - да
- быстрый ремонт - да
- выдать с ремонта - нет
- добавить файлы - да
- добавить описание ремонта - нет
- отправить на списание - да

.


