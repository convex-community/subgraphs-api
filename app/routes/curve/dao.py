from flask_restx import Resource, Namespace
from models.curve.dao import DaoProposal
from services.curve.dao import get_all_proposals
from utils import convert_marshmallow

api = Namespace("dao", description="DAO endpoints")
proposals = api.model("DAO Proposals", convert_marshmallow(DaoProposal))


def check_exists(func):
    def wrapped(*args, **kwargs):
        data = func(*args, **kwargs)
        if not data:
            api.abort(404)
        return data

    return wrapped


@api.route("/proposals")
@api.doc(description="Get all submitted proposals")
class ProposalList(Resource):
    @api.marshal_with(proposals)
    def get(self):
        return get_all_proposals()


@api.route("/proposals/<int:id>")
@api.doc(description="Get full details of a proposal")
@api.param("chain", "Chain to query for")
@api.response(404, "Proposal not found")
class FactoryList(Resource):
    @check_exists
    def get(self, id):
        return 0  # get_proposal_details(id)
