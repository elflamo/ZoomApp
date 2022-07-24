#!/bin/sh

git pull origin master

sudo systemctl daemon-reload
sudo systemctl restart gunicorn
sudo systemctl restart nginx

sudo pkill -f "celery"

source venv/bin/activate

cd zoomproject/

python manage.py makemigrations
python manage.py migrate

> log.json
> nohup.out
> worker.log
> Exception.txt

nohup celery -A zoomproject worker --loglevel=info --logfile=worker.log -Q request_queue --concurrency=1 -n worker1@h &

echo "Done"