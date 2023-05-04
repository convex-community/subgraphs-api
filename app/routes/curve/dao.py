from flask_restx import Resource, Namespace
from routes import cache
from main.const import OWNERSHIP, PARAMETER
from models.curve.dao import (
    DaoProposal,
    flask_restx_dao_proposal_details,
    UserLock,
    UserBalance,
    DaoVote,
    Gauge,
    Emission,
)
from services.curve.dao import (
    get_all_proposals,
    get_proposal_details,
    get_user_locks,
    get_user_balance,
    get_user_votes,
    get_user_proposals,
    get_all_gauges,
    get_emissions_by_gauge,
    get_emissions_by_pool,
)
from utils import convert_marshmallow
from flask_restx import fields

api = Namespace("dao", description="DAO endpoints")
proposals = api.model("DAO Proposals", convert_marshmallow(DaoProposal))
votes = api.model("Vote", convert_marshmallow(DaoVote))
gauges = api.model("Gauge", convert_marshmallow(Gauge))
emissions = api.model("Emission", convert_marshmallow(Emission))
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
class DetailedOwnershipProposal(Resource):
    @api.marshal_with(detailed_proposal)
    # @cache.cached(timeout=60 * 2)
    def get(self, voteid):
        proposal = get_proposal_details(voteid, OWNERSHIP)
        if not proposal:
            api.abort(404)
        return proposal


@api.route("/proposals/parameter/<int:voteid>")
@api.doc(description="Get full details of a parameter proposal")
@api.param("voteid", "ID of proposal to query for")
@api.response(404, "Proposal not found")
class DetailedParameterProposal(Resource):
    @api.marshal_with(detailed_proposal)
    @cache.cached(timeout=60 * 2)
    def get(self, voteid):
        proposal = get_proposal_details(voteid, PARAMETER)
        if not proposal:
            api.abort(404)
        return proposal


@api.route('/<regex("[A-z0-9]+"):user>/locks/history')
@api.doc(description="Return historical vote escrow actions by a user")
@api.param("user", "User address")
class UserHistoricalLocks(Resource):
    @api.marshal_list_with(user_locks, envelope="locks")
    def get(self, user):
        return get_user_locks(user.lower())


@api.route('/<regex("[A-z0-9]+"):user>/locks/balance')
@api.doc(description="Return historical vote escrow actions by a user")
@api.param("user", "User address")
class GetUserBalance(Resource):
    @api.marshal_with(user_balance)
    def get(self, user):
        return get_user_balance(user.lower())


@api.route('/<regex("[A-z0-9]+"):user>/votes')
@api.doc(description="Return all of a user's votes")
@api.param("user", "User address")
class GetUserVotes(Resource):
    @api.marshal_list_with(votes, envelope="votes")
    def get(self, user):
        return get_user_votes(user.lower())


@api.route('/<regex("[A-z0-9]+"):user>/proposals')
@api.doc(description="Return all of a user's proposals")
@api.param("user", "User address")
class GetUserProposals(Resource):
    @api.marshal_list_with(proposals, envelope="proposals")
    def get(self, user):
        return get_user_proposals(user.lower())


@api.route("/gauges")
@api.doc(description="Get the list of all gauges")
class GetAllGauges(Resource):
    @api.marshal_list_with(gauges, envelope="gauges")
    @cache.cached(timeout=60 * 2)
    def get(self):
        return get_all_gauges()


@api.route('/emissions/gauge/<regex("[A-z0-9]+"):gauge>')
@api.doc(description="Get a gauge's historical weekly emissions")
@api.param("gauge", "Gauge address")
class GetGaugeEmissions(Resource):
    @api.marshal_list_with(emissions, envelope="emissions")
    def get(self, gauge):
        return get_emissions_by_gauge(gauge.lower())


@api.route('/emissions/pool/<regex("[A-z0-9]+"):pool>')
@api.doc(description="Get a pool's historical weekly emissions")
@api.param("pool", "Pool address")
class GetPoolEmissions(Resource):
    @api.marshal_list_with(emissions, envelope="emissions")
    def get(self, pool):
        return get_emissions_by_pool(pool.lower())
