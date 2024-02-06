# InstaBot server

### How to install dependencies

```pip install -r requirements.txt```

### How to run Locally
```python -m uvicorn main:app --reload```

### How to run on Server
```python3 -m uvicorn main:app --host 0.0.0.0 --port 8000```

### How to extract dependencies

```pip freeze > requirements.txt```

### API documentations

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

[http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
