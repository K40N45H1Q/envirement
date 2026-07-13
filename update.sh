cd ~/www

GIT_OUTPUT=$(git pull)

echo "$GIT_OUTPUT"

if [[ "$GIT_OUTPUT" == *"Already up to date."* ]]; then
    exit 0
fi

npm --prefix ~/www/frontend install
npm --prefix ~/www/frontend run build

rm -rf /var/www/app/frontend/*
cp -a ~/www/frontend/dist/. /var/www/app/frontend/

cd ~/www/backend

PIP_DISABLE_PIP_VERSION_CHECK=1 .venv/bin/python -m pip install -r requirements.txt

pkill -f "python run.py" 2>/dev/null || true
sleep 1

nohup .venv/bin/python run.py > /dev/null 2> errors.log &

sleep 3

echo "Update completed successfully."