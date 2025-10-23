# IT-project8
cd "/Users/hanzhang/Documents/学习/2025/第二学期/COMP30022/ass1/代码/IT-project8 19.34.34"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install django==5.2.6 djangorestframework django-cors-headers pandas openpyxl reportlab mysqlclient
python manage.py migrate
python manage.py runserver 0.0.0.0:8000

cd "/Users/hanzhang/Documents/学习/2025/第二学期/COMP30022/ass1/代码/IT-project8-1 19.34.34/frontend"
npm install
npm run dev
