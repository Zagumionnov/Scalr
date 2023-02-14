VENV := venv
all: venv

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	./$(VENV)/bin/pip install -r requirements.txt

venv: $(VENV)/bin/activate
run: venv worker
	./$(VENV)/bin/python3 app.py

worker: venv
	./$(VENV)/bin/python3 app/worker.py > ./worker.log 2>&1 &

clean:
	rm -rf $(VENV)
	find . -type f -name '*.pyc' -delete

.PHONY: all venv run clean