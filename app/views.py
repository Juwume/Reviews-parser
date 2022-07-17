from app import app

@app.route('/')
def index():
    return {'message': 'Hello, this is my diploma work'}
