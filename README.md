# Sumit-Engineering-django
======================================
Sumit Engineering – Django Web Project
======================================

Project overview
----------------
A Django-based catalogue site that showcases industrial kitchen equipment,
lets users browse products, add items to a cart, and submit price inquiries.

Tech-stack snapshot (env packages)
----------------------------------
Python      : 3.10.11
asgiref==3.8.1
certifi==2025.7.14
charset-normalizer==3.4.2
Django==5.2.3
idna==3.10
pillow==11.2.1
pyngrok==7.2.12
PyYAML==6.0.2
razorpay==1.4.2
requests==2.32.4
sqlparse==0.5.3
typing_extensions==4.14.0
tzdata==2025.2
urllib3==2.5.0

Core features
-------------
• Product listings with category filters  
• Shopping cart & checkout flow  
• Price-inquiry / contact form  
• Responsive UI  
• Admin panel for products & orders  

Quick start (local)
-------------------
1. Clone repo  
   git clone https://github.com/code-dhruv-l/Sumit-Engineering-django.git  
   cd Sumit-Engineering-django  

2. Create & activate virtual-env  
   python -m venv env  
   env\Scripts\activate        # Linux/mac: source env/bin/activate  

3. Install exact dependencies  
   pip install -r requirements.txt  

4. Migrate & collect static  
   python manage.py migrate  
   python manage.py collectstatic --noinput  

5. (Optional) superuser  
   python manage.py createsuperuser  

6. Run dev server  
   python manage.py runserver  
   Browse http://127.0.0.1:8000

Environment variables (dev)
---------------------------
DEBUG=True
SECRET_KEY=your-secret-here
DATABASE_URL=sqlite:///db.sqlite3

Contributing
------------
Fork → branch → commit → push → pull-request

License
-------
MIT License