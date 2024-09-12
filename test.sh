
mkdir .venv

pip install pipenv
pip install pytest-cov
pip install pytest-html
pip install pytest-xdist
pipenv --three

pipenv run pip3 install -r requirements.txt #  -i xxx --trusted-host xxx
echo "install all success"

# 执行 并 统计覆盖率
pipenv run pytest --cov=. --cov-report=html:reports/coverage_report --cov-config=.coveragerc --html=reports/testresult.html --self-contained-html
