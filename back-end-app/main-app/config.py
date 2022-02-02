
db_user = 'postgres'
db_password = 'sarna'
db_host = 'localhost'
db_host_dock = 'postgress'
db_port = 5432
db_name = 'sarna'

DATABASE_URI = f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
DATABASE_URI_DOCKER = f'postgresql+psycopg2://{db_user}:{db_password}@{db_host_dock}:{db_port}/{db_name}'