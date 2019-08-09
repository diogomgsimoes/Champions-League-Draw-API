from sanic.response import json
from sanic import Blueprint
import home_page
import db_final

bp2 = Blueprint('api', url_prefix='api/champions-league/draw')
groups_str = "ABCDEFGH"

# rota inicial
# display: calendario e regras
@bp2.route('/')
async def bp_root(request):
    result = ({"Calendar": home_page.calendar},
              {"Rules": home_page.rules})
    return json(result)

@bp2.route('/groups')
async def bp_root1(request):
    db_final.clear_groups(db_final.objGroups)
    lst = db_final.objectConvGroups()
    draw = db_final.Draw()
    draw.body(db_final.objPots, lst)
    return json(db_final.objGroups)