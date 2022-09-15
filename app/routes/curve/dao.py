from flask_restx import Resource, Namespace

from main.const import OWNERSHIP
from models.curve.dao import DaoProposal, DaoDetailedProposal
from services.curve.dao import get_all_proposals, get_proposal_details
from utils import convert_marshmallow

api = Namespace("dao", description="DAO endpoints")
proposals = api.model("DAO Proposals", convert_marshmallow(DaoProposal))
detailed_proposal = api.model(
    "DAO Proposal Details", convert_marshmallow(DaoDetailedProposal)
)


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
    @api.marshal_list_with(proposals, envelope="proposals")
    def get(self):
        return get_all_proposals()


@api.route("/proposals/ownership/<int:voteid>")
@api.doc(description="Get full details of an ownership proposal")
@api.param("id", "ID of proposal to query for")
@api.response(404, "Proposal not found")
class DetailedProposal(Resource):
    @api.marshal_with(detailed_proposal)
    def get(self, voteid):
        proposal = get_proposal_details(voteid, OWNERSHIP)
        if not proposal:
            api.abort(404)
        return proposal
