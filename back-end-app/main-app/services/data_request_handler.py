from typing import List
from flask_restful import Api, Resource, reqparse
from datetime import datetime, timedelta
import random
import pika
from sqlalchemy import func, desc, asc
from werkzeug.wrappers import Request
from app import db
from models import Candidate, Company, Action, Future, Prediction, Stock, Apisource, UserDataPoint, UserDataPrediction, UserRequest

from misc import dane_z_nikad

class PredictRequestHandler(Resource):

  def get(self, symbol=None):
    return self.add_company(symbol)

  def add_company(self, symbol):
  
    credentials = pika.PlainCredentials('sarna', 'sarna')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue='pred_queue_0', durable=True)
    channel.basic_publish(
        exchange='',
        routing_key='pred_queue_0',
        body=symbol,
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ))
    connection.close()
    return {'msg': 'adding'}



class AddCompanyRequestHandler(Resource):

  def get(self, symbol=None):
    return self.add_company(symbol)

  def add_company(self, symbol):
    
    results = Company.query.filter(Company.symbol == symbol).all()
    if len(results)> 0:
      company = results[0]
      return {'msg': 'present', 'name': company.company_name}
    credentials = pika.PlainCredentials('sarna', 'sarna')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue='task_queue', durable=True)
    channel.basic_publish(
        exchange='',
        routing_key='task_queue',
        body=symbol,
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ))
    connection.close()
    return {'msg': 'adding'}

class OwnPredictionRequestHandler(Resource):

  def get(self, request_id=None):
    if not request_id:
        return {'msg': 'Provide request id!'}
    try:
      request_id = int(request_id)
    except:
      return {'msg': 'Provide propper request id!'}
    results = UserRequest.query.filter(UserRequest.request_id == request_id).all()
    if len(results) == 0:
      return {'msg':'No request!'}
    request:UserRequest
    request = results[0]
    
    if request.state == 0:
      return {'msg': 'fine', 'state':'waiting in queue'}
    if request.state == 1:
      return {'msg': 'fine', 'state':'processing', 'progress':request.progress}

    actions = UserDataPoint.query.filter(UserDataPoint.request_id==request.id).order_by(desc(UserDataPoint.timestamp)).limit(100)[::-1]
    predict = UserDataPrediction.query.filter(UserDataPrediction.request_id==request.id).order_by(desc(UserDataPrediction.timestamp))[::-1]

    actions = [(e, round(float(action.value / 1000.0), 2)) for e, action in enumerate(actions)]
    alen = len(actions)
    predict = [(alen + e - 1, round(float(pred.value / 1000.0), 2)) for e, pred in enumerate(predict)]

    data = {'request': request.request_id}
    data['data'] = {t[0]:t[1] for t in actions[-80:]}
    data['predict'] = {t[0]:t[1] for t in predict}

    return data


class PopularCompanyRequestHandler(Resource):

  def get(self, symbol=None):
    return self.add_company(symbol)

  def add_company(self, symbol):
    companies: List[Company]
    companies = Company.query.limit(4)
    
    return {'popular': [[x.symbol, x.company_name] for x in companies]}


class ActionDataRequestHandler(Resource):

  def get(self, company=None):
    return self.fetch_company_data(company)

  def fetch_company_data(self, company_name):
    
    results = Company.query.filter(Company.company_name == company_name).all()
    if len(results)> 0:
      company = results[0]
    else:
      results = Company.query.filter(Company.symbol == company_name).all()
      if len(results)> 0:
        company = results[0]
      else:
        return {'company': 'NONE', 'data': 'NONE', 'predict': 'NONE'}

    data = {'company': company.company_name}
    actions = Action.query.filter(Action.company_id==company.id).order_by(desc(Action.timestamp)).limit(100)[::-1]
    future = Future.query.filter(Future.company_id==company.id).all()
    if len(future) > 0:
      future = future[0]
      predict = Prediction.query.filter(Prediction.company_id==future.id).order_by(desc(Prediction.timestamp))[::-1]
    else:
      predict = []

    actions = [(datetime.fromtimestamp(action.timestamp).strftime('%Y.%m.%d'), round(float(action.value / 1000.0), 2)) for e, action in enumerate(actions)]
    predict = [(datetime.fromtimestamp(pred.timestamp).strftime('%Y.%m.%d'), round(float(pred.value / 1000.0), 2)) for e, pred in enumerate(predict)]
    data['data'] = {t[0]:t[1] for t in actions}

    data['predict'] = {t[0]:t[1] for t in predict}

    return data
  

with open('stock_combined.txt', 'r', encoding='utf8') as fi:
  candidates = sorted([x.split(';') for x in fi], key=lambda y: y[1])

class CandidateRequestHandler(Resource):

  def get(self,):
    return self.fetch_company_data()

  def fetch_company_data(self):
    
    companies = set(c.symbol for c in Company.query.all())
    candidates = list(filter(lambda x: x[1] not in companies, [(c.name, c.symbol) for c in  Candidate.query.order_by(asc(Candidate.name)).all()]))
    return {'candidates':candidates}
  
class CurrentModelRequestHandler(Resource):

  def get(self,):
    return [{'name':'Model prosty', 'id':0, 'desc':'Szybki model przystosowany do predykcji na krótkich okresach czas.'},
            {'name':'Model zaawansowany', 'id':1, 'desc':'Rozbudowany model posiadający wyższą skuteczność dla większych okresów czasu.'},
            {'name':'Model niewielkich różnic', 'id':2, 'desc':'Prosty model przystosowany do danych o niższej dynamice. '}]
  

class CompanyDataRequestHandler(Resource):

  def get(self):
    data = {}
    data['companies'] = self.fetch_companies_data()
    return data

  def fetch_companies_data(self):
    companies = Company.query.all()
    data = []
    
    for company in Company.query.all():
      company:Company
      actions = Action.query.filter(Action.company_id==company.id).order_by(desc(Action.timestamp))[:2]
      if len(actions) > 0:
        value = actions[1].value / 1000.0
        groing_by = (actions[0].value - actions[1].value) / 1000.0
        if groing_by > 0:
          is_groing = 'yes'
        else:
          is_groing = 'no'
      else:
        is_groing = 'unknown'
        groing_by = 0
        value = 0
      data.append({'name':company.company_name, 'symbol':company.symbol, 'growing':is_groing, 'growing_by':groing_by, 'value':value})
    return data
        

  def post(self):
    return {'ERROR':'NOT IMPLEMENTED!'}