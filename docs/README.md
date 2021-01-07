# Build document
---

## install
```
python -m pip install Sphinx
```

## Add a docs/requirements.txt
* sphinx

## start
```
mkdir docs
cd docs/
sphinx-quickstart
```

## configure
* uncomment following lines in source/conf.py
```
# import os
# import sys
# sys.path.insert(0, os.path.abspath('../springframework'))
```
* add extensions and theme

## create modules
```
sphinx-apidoc -o source/reference ../springframework -f
cp source/reference/modules.rst source/
```

## re-structure
```
python run.py -v source/reference/springframework*.rst
```

## write index
* modify index.rst

## build at local
```
make html
```
