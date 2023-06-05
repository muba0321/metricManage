指标中心当前版本1.0.3
python3.10（如果使用pycharm的话需要2023版本）
asgiref==3.6.0
Django==4.1.7
django-cors-headers==3.14.0
djangorestframework==3.14.0
install==1.3.5
pytz==2023.3
sqlparse==0.4.3
tzdata==2023.3
requests~=2.30.0

部署流程：
1.修改后端的setting.xml里面的数据库信息以及最下面的准入IP加端口

2.docker load -i 容器包

3.docker run XXXX

4.docker cp 代码包  容器id:/opt

5.docker exec -it 容器id   /bin/bash

6.到代码包内，bash djang_run.sh,输出日志在monitor.logs里面
