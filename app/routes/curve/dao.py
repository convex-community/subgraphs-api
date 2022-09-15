from flask_restx import Resource, Namespace
from routes import cache
from main.const import OWNERSHIP
from models.curve.dao import (
    DaoProposal,
    flask_restx_dao_proposal_details,
    UserLock,
    UserBalance,
    DaoVote,
)
from services.curve.dao import (
    get_all_proposals,
    get_proposal_details,
    get_user_locks,
    get_user_balance,
)
from utils import convert_marshmallow
from flask_restx import fields

api = Namespace("dao", description="DAO endpoints")
proposals = api.model("DAO Proposals", convert_marshmallow(DaoProposal))
votes = api.model("Votes", convert_marshmallow(DaoVote))
flask_restx_dao_proposal_details["votes"] = fields.List(fields.Nested(votes))
detailed_proposal = api.model(
    "DAO Proposal Details", flask_restx_dao_proposal_details
)
user_locks = api.model(
    "User vote escrow actions", convert_marshmallow(UserLock)
)
user_balance = api.model("User lock balance", convert_marshmallow(UserBalance))


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
    @cache.cached(timeout=60 * 2)
    def get(self):
        return get_all_proposals()


@api.route("/proposals/ownership/<int:voteid>")
@api.doc(description="Get full details of an ownership proposal")
@api.param("voteid", "ID of proposal to query for")
@api.response(404, "Proposal not found")
class DetailedProposal(Resource):
    @api.marshal_with(detailed_proposal)
    @cache.cached(timeout=60 * 2)
    def get(self, voteid):
        proposal = get_proposal_details(voteid, OWNERSHIP)
        if not proposal:
            api.abort(404)
        return proposal


@api.route('/locks/<regex("[a-z0-9]+"):user>/history')
@api.doc(description="Return historical vote escrow actions by a user")
@api.param("user", "User address")
class UserHistoricalLocks(Resource):
    @api.marshal_list_with(user_locks, envelope="locks")
    def get(self, user):
        return get_user_locks(user.lower())


@api.route('/locks/<regex("[a-z0-9]+"):user>/balance')
@api.doc(description="Return historical vote escrow actions by a user")
@api.param("user", "User address")
class GetUserBalance(Resource):
    @api.marshal_with(user_balance)
    def get(self, user):
        return get_user_balance(user.lower())
