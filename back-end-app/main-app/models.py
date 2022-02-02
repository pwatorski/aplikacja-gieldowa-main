from base_app import db
from datetime import datetime


class Apisource(db.Model):
    __tablename__ = 'api_source'
    id = db.Column(db.Integer, primary_key=True)
    api_name = db.Column(db.String(80), unique=True, nullable=False)
    last_checked = db.Column(db.BigInteger, nullable=False)

    def __init__(self, api_name, last_checked=None) -> None:
        super().__init__()
        self.api_name = api_name
        if last_checked:
            self.last_checked = last_checked
        else:
            self.last_checked = int(datetime.timestamp(datetime.now()))


class Stock (db.Model):
    __tablename__ = 'stock'
    id = db.Column(db.Integer, primary_key=True)
    stock_name = db.Column(db.String(80), unique=False, nullable=False)
    last_checked = db.Column(db.BigInteger, nullable=False)
    api_id = db.Column(db.Integer, db.ForeignKey('api_source.id'))
    
    def __init__(self, stock_name, api_id, last_checked=None) -> None:
        super().__init__()
        self.stock_name = stock_name
        if last_checked:
            self.last_checked = last_checked
        else:
            self.last_checked = int(datetime.timestamp(datetime.now()))
        self.api_id = api_id


class Company (db.Model):
    __tablename__ = 'company'
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(80), unique=False, nullable=False)
    symbol = db.Column(db.String(80), unique=True, nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'))

    def __init__(self, company_name, symbol, stock_id) -> None:
        super().__init__()
        self.company_name = company_name
        self.symbol = symbol
        self.stock_id=stock_id

class UserRequest (db.Model):
    __tablename__ = 'user_request'
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.BigInteger, unique=True, nullable=False)
    state = db.Column(db.Integer)
    progress = db.Column(db.Integer)
    def __init__(self, request_id, state, progress) -> None:
        super().__init__()
        self.request_id = request_id
        self.state = state
        self.progress = progress

class UserDataPoint (db.Model):
    __tablename__ = 'user_data_point'
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.BigInteger, db.ForeignKey('user_request.id'))
    value = db.Column(db.Integer, unique=False, nullable=False)
    timestamp = db.Column(db.Integer, unique=False, nullable=False) 
    def __init__(self, request_id, value, timestamp) -> None:
        super().__init__()
        self.request_id = request_id
        self.value = value
        self.timestamp = timestamp

class UserDataPrediction (db.Model):
    __tablename__ = 'user_pred'
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.BigInteger, db.ForeignKey('user_request.id'))
    value = db.Column(db.Integer, unique=False, nullable=False)
    timestamp = db.Column(db.Integer, unique=False, nullable=False) 

    def __init__(self, request_id, value, timestamp) -> None:
        super().__init__()
        self.request_id = request_id
        self.value = value
        self.timestamp=timestamp


class Future (db.Model):
    __tablename__ = 'future'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    timestamp = db.Column(db.BigInteger, nullable=False)

    def __init__(self, company_id, timestamp, stock_id) -> None:
        super().__init__()
        self.company_id = company_id
        self.timestamp=timestamp

class Prediction (db.Model):
    __tablename__ = 'prediction'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('future.id'))
    timestamp = db.Column(db.BigInteger, nullable=False)
    value = db.Column(db.Integer, unique=False, nullable=False)

    def __init__(self, company_id, timestamp, value) -> None:
        super().__init__()
        self.company_id = company_id
        self.timestamp=timestamp
        self.value = value

class Candidate (db.Model):
    __tablename__ = 'candidate'
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(160), nullable=False)
    def __init__(self, company_id, symbol, name) -> None:
        super().__init__()
        self.symbol=symbol
        self.name = name


class Action (db.Model):
    __tablename__ = 'action'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, unique=False, nullable=False)
    timestamp = db.Column(db.BigInteger, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    
    def __init__(self, value, timestamp, company_id) -> None:
        super().__init__()
        self.value = value
        self.timestamp = timestamp
        self.company_id = company_id