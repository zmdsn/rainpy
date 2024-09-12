
cd example

pip install ipython
pip install pipenv
pip install pytest

echo python --version
echo "install all success"

git config user.name example
git config user.email zmdsn@126.com
rm -rf .git
git init
git add .
git commit -m "generate by rainpy"
