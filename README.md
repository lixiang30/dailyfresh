# dailyfresh

###项目框架搭建   

1.新建虚拟环境：mkvirtualenv dailyfresh   

2.进入虚拟环境:workon dailyfresh   

3.安装相应的软件   

4.新建项目:django-admin startproject dailyfresh   

5.新建应用:python manage.py startapp user/cart/order/goods[表示新建了四个应用，分别为user、cart、order、goods]   

最后，新建一个package,将四个应用拖到package中，再对settings.py文件进行想象的配置。接下来就是在各个应用中创建一个urls.py文件，在主urls.py文件中配置各子url路径，完成后就可以建模了．
