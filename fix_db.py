# 读取settings.py
with open("itp8/settings.py", "r") as f:
    content = f.read()

# 替换MySQL为SQLite
old_config = """DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dataforitp8',
        'USER':'shuxuan1',
        'PASSWORD':'Guardian1127',
        'HOST':'127.0.0.1',
        'PORT':'3306',
    }
}"""

new_config = """DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}"""

content = content.replace(old_config, new_config)

# 写回文件
with open("itp8/settings.py", "w") as f:
    f.write(content)

print("数据库配置已临时改为SQLite")
