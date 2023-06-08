from dataclasses import dataclass
import marshmallow_dataclass
from typing import List
from sqlalchemy import Column, Integer, Float, String, Boolean
from sqlalchemy.dialects.postgresql import ARRAY
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from main import db


class CurvePool(db.Model):
    __tablename__ = "curve_pool"

    id = Column(String, primary_key=True)
    address = Column(String)
    name = Column(String)
    symbol = Column(String)
    poolType = Column(String)
    assetType = Column(Integer)
    chain = Column(String)
    lpToken = Column(String)
    coins = Column(ARRAY(String))
    coinNames = Column(ARRAY(String))
    coinDecimals = Column(ARRAY(Integer))
    isV2 = Column(Boolean)
    cumulativeVolumeUSD = Column(Float)
    cumulativeFeesUSD = Column(Float)
    virtualPrice = Column(Float)
    baseApr = Column(Float)


class CurvePoolSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = CurvePool
        load_instance = True


@dataclass
class CurvePoolName:
    address: str
    name: str


CurvePoolNameSchema = marshmallow_dataclass.class_schema(CurvePoolName)


@dataclass
class CurvePoolNameChain:
    address: str
    name: str
    chain: str


CurvePoolNameChainSchema = marshmallow_dataclass.class_schema(
    CurvePoolNameChain
)
