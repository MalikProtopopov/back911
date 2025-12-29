# 🔧 Исправление конфликта git на сервере

## Проблема:
Git pull не может выполниться, потому что на сервере уже есть файлы `deploy.sh` и `update.sh`, которые конфликтуют с версиями из репозитория.

## Решение - выполните на сервере:

```bash
cd ~/back911

# 1. Удалить конфликтующие файлы (они будут заменены версиями из репозитория)
rm -f deploy.sh update.sh

# 2. Теперь можно сделать git pull
git pull origin main

# 3. Сделать скрипты исполняемыми
chmod +x deploy.sh update.sh

# 4. Запустить деплой
./deploy.sh
```

## Альтернативный вариант (сохранить локальные изменения):

```bash
cd ~/back911

# 1. Сохранить локальные версии (если нужно)
mv deploy.sh deploy.sh.local
mv update.sh update.sh.local

# 2. Сделать git pull
git pull origin main

# 3. Сравнить файлы (если нужно)
diff deploy.sh deploy.sh.local
diff update.sh update.sh.local

# 4. Удалить локальные версии
rm deploy.sh.local update.sh.local

# 5. Сделать скрипты исполняемыми
chmod +x deploy.sh update.sh

# 6. Запустить деплой
./deploy.sh
```

## Быстрое решение одной командой:

```bash
cd ~/back911 && rm -f deploy.sh update.sh && git pull origin main && chmod +x deploy.sh update.sh && ./deploy.sh
```

