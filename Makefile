run:
	Q_APP_SECRET_KEY='_5#y2L"F4Q8z\n\xec]/l3' python run_server.py

isort:
	isort -rc .

black:
	black --target-version py38 .

flake:
	flake8 .

test_unit:
	Q_APP_SECRET_KEY='testkey' pytest -sv test
    
