# -*- coding: utf-8 -*-

from .db.db import Db as db


class Index(db.Model):
    __tablename__ = 'index'
    symbol = db.Column(db.String(6), unique=True, nullable=False, primary_key=True)
    company = db.Column(db.String(60),nullable=False)
    sector = db.Column(db.String(80),nullable=False)
    industry = db.Column(db.String(60),nullable=False)


class Stock(db.Model):
    __tablename__ = 'stock'
    id = db.Column(db.String(40), unique=True, nullable=False, primary_key=True)
    symbol = db.Column(db.String(6), db.ForeignKey("index.symbol"), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    open = db.Column(db.Float, nullable=True)
    high = db.Column(db.Float, nullable=True)
    low = db.Column(db.Float, nullable=True)
    close = db.Column(db.Float, nullable=True)
    adjusted = db.Column(db.Float, nullable=True)
    volume = db.Column(db.Integer, nullable=True)
