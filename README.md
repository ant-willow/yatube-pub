# yatube
## Платформа для блогов
### Незарегистрированным пользователям доступно:
Просмотр постов, список сообществ
### Зарегистрированным пользователям доступно:
Публикация постов

Подписываться на авторов, сообщества, посты

Создавать сообщества, комментировать посты

## Инструкция для развертывания:
 - Клонировать себе репозиторий
 - Заполнить секреты в репозитории:\
	 **USER** - имя пользователя для подключения к серверу\
	 **HOST** - IP-адрес сервера\
	 **SSH_KEY** - приватный ключ\
	 **PASSPHRASE** - фраза-пароль для ключа\
	 **DOCKER_USERNAME** - имя пользователя Docker Hub\
	 **DOCKER_PASSWORD** - пароль от Docker Hub\
	 **SECRET_KEY** - секретный ключ Django\
 - Сделать push

После удачного запуска, проект будет доступен по адресу HOST.
