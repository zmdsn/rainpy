# generate API tokens, then make ~/.pypirc 
python setup.py sdist
twine upload dist/*