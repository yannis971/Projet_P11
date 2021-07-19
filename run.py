import os
from webapp import app

if __name__ == "__main__":
    os.environ['WERKZEUG_RUN_MAIN'] = 'true'
    app.run(debug=False)
