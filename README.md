Это проект для Яндекс академии.
Для того, чтобы развернуть проект на сервере нужно:
1. Выполнить команду sudo apt-get install python3 python3-pip python3-dev gcc git nginx
2. git clone [ссылка на этот репозиторий]
3. Логин и пароль
4. nano имя_скрипта
5. #!/bin/bash
cd глобальный путь до проекта
sudo /usr/bin/python3 app.py  > /dev/null
6. chmod a+x имя_скрипта
7. crontab -e
   @reboot путь к скрипту и его имя
8. mkdir certs
9. openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 -keyout certs/key.pem -out certs/cert.pem
10. sudo rm /etc/nginx/sites-enabled/default
11. sudo nano /etc/nginx/sites-enabled/flask
12. server {
    listen 80;
    server_name _;
    location / {
        return 301 https://$host$request_uri;
    }
}
server {
    listen 443 ssl;
    server_name _;

    ssl_certificate путь до certs/cert.pem;
    ssl_certificate_key путь до certs/key.pem;

    access_log /var/log/catsanddogs_access.log;
    error_log /var/log/catsanddogs_error.log;

    location / {
        proxy_pass http://localhost:8000;
        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
13. sudo reload
15. Ждём минуту, и сервер работает

Инструкция по запуску тестов:
1. После всех действий, проделанных выше, можно перейти в папку tests/ в проекте (не на сервере), перейти в один из файлов и изменить в ссылке ip на ip вашего сервера
2. Запустить
