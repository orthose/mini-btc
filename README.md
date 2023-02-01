# Introduction
Projet de création d'une blockchain bitcoin locale simplifiée
basée sur une architecture pair à pair construite manuellement.

# Architecture
![Architecture](./archi.jpg)

# Environnement virtuel
```shell
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

# Exécution des tests
```shell
cd mini-btc
export PYTHONPATH=`pwd`
cd tests
python3 tests_node.py
```
