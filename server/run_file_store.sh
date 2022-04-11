source $(pipenv --venv)/bin/activate
cd ../store/
nohup python -m http.server 8989 &
