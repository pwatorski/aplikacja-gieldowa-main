from datetime import timedelta
import random
from typing import List
from app import db
from models import Apisource, Stock, Company, Action
from misc import dane_z_nikad
try:
    from tqdm import tqdm
    TQDM=True
except:
    TQDM=False
    print("Consider instaling tqdm package for your Python interpreter:\npy -m pip install tqdm")

def clear_db(db):
    print('Removing Action, Company, Stock, Apisource tables...')
    try:
        db.session.query(Action).delete()
    except:
        pass
    try:
        db.session.query(Company).delete()
    except:
        pass
    try:
        db.session.query(Stock).delete()
    except:
        pass
    try:
        db.session.query(Apisource).delete()
    except:
        pass
    print('Creating Action, Company, Stock, Apisource tables...')
    db.create_all()
    try:
        db.session.commit()
    except:
        pass

def create_apisource(db, name:str):
    apisource = Apisource(name)
    db.session.add(apisource)
    db.session.commit()
    return apisource.id

def create_stock(db, name:str, apisource_id:int):
    stock = Stock(name, apisource_id)
    db.session.add(stock)
    db.session.commit()
    return stock.id

def create_company(db, name:str, stock_id:int):
    company = Company(name, name, stock_id)
    db.session.add(company)
    db.session.commit()
    return company.id

def create_actions(db, company_id, steps=1000, base_value=400, fluctuation=100):
    for timestamp, value in dane_z_nikad(steps=steps, beg_val=base_value, fluctuation=fluctuation, stringify=False, step_time=timedelta(hours=1)).items():
        a = Action(value, timestamp, company_id)
        db.session.add(a)
    db.session.commit()

def build_company_and_actions(company_name, stock_id, steps, verbouse=True):
    if verbouse:
        print(f'\tCreating {company_name}...')
    company_id = create_company(db, company_name, stock_id)
    base = random.randint(10, 1000)
    create_actions(db, company_id, steps=steps, base_value=base, fluctuation=base/100)
    if verbouse:
        print(f'\t\tInserted {steps} Action records.')

def populate(db, companies:List[str]=[]):
    print('Clearing db...')
    clear_db(db)
    print('Creating apisource...')
    api_id = create_apisource(db, 'Yahoo')
    print('Creating stock...')
    stock_id = create_stock(db, 'Some Stock', api_id)
    print('Creating companies:')
    steps = 1000

    if companies is None or len(companies) == 0:
        companies = ['cdp', 'tesla', 'game_stop']
        companies.extend([f'company{e+3}' for e in range(64-len(companies))])

    if TQDM:
        for company in tqdm(companies):
            build_company_and_actions(company, stock_id, steps, verbouse=False)
    else:
        for company in tqdm(companies):
            build_company_and_actions(company, stock_id, steps)
    print('Finished :)')


random.seed(42)

populate(db)