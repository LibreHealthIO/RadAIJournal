from app import app, db
from app.models import User,Report

@app.shell_context_processor
def make_shell_context():
    return {'db':db,'User':User,'Report':Report}

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5000)
