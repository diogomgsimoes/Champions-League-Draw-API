from sanic import Sanic
from blueprint import bp2
import db_final

app = Sanic(__name__)
app.blueprint(bp2)

if __name__ == '__main__':
    db_final.connect()
    app.run(host='0.0.0.0', port=8000, debug=True)
