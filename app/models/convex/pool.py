from dataclasses import dataclass
import marshmallow_dataclass

from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.dialects.postgresql import ARRAY
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from main import db


class ConvexPool(db.Model):
    __tablename__ = "convex_pool"

    id = Column(String, primary_key=True)
    name = Column(String)
    token = Column(String)
    lpToken = Column(String)
    swap = Column(String)
    gauge = Column(String)
    crvRewardsPool = Column(String)
    isV2 = Column(Boolean)
    creationDate = Column(Integer)
    creationBlock = Column(Integer)
    tvl = Column(Float)
    curveTvlRatio = Column(Float)
    baseApr = Column(Float)
    crvApr = Column(Float)
    cvxApr = Column(Float)
    extraRewardsApr = Column(Float)
    extraRewards = Column(ARRAY(String))


class ConvexPoolSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ConvexPool
        load_instance = True  # Optional: deserialize to model instances


@dataclass
class ConvexPoolName:
    id: str
    name: str


ConvexPoolNameSchema = marshmallow_dataclass.class_schema(ConvexPoolName)
