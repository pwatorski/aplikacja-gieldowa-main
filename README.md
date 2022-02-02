# aplikacja-gieldowa

1)Front(angular) ...front-end-app/web-app$ ng serve

2)back (flask) ...back-end-app/main-app$ flask run

3)reszta backendu ...back-end-app$ sudo docker-compose up

Do debugu można sobie wykomentowac workera z docker-compose i odpalać go z ręki komendą:
python3 app.py
z folderu workera


Docker (wszystko w back-end-app/):

Usunięcie wszystkich obrazów, dysków itd, do świeżego builda:
sudo docker system prune --all --volumes -f

Budowanie workerów:

sudo docker build ./stockapiworker/ -t stockapiworker:latest --no-cache
sudo docker build ./basicpredworker/ -t basicpredworker:latest --no-cache

jak jakiegos obrazu brakuje i o niego krzyczy to tylko nazwy odpowiednie wstawić:

sudo docker build ./brakujacy_obraz/ -t brakujacy_obraz:latest --no-cache


jeśli docker się wykrzacza na postgresie należy zabić postgresa:

wyszukujesz pida procesu:
sudo ss -lptn 'sport = :5432'

wyskoczy cos takiego, albo podobnego:
State        Recv-Q       Send-Q             Local Address:Port              Peer Address:Port       Process                                        
LISTEN       0            4096                     0.0.0.0:5432                   0.0.0.0:*           users:(("docker-proxy",pid=43397,fd=4))

w zakładce 'Process' mamy pid=jakiś_numer_pid

potem puszczamy:
sudo kill -9 jakiś_numer_pid

potem można odpalać dockera

http://127.0.0.1:5000/flask/add_company/TSLA
http://127.0.0.1:5000/flask/add_company/RBLX
http://127.0.0.1:5000/flask/add_company/PFE
http://127.0.0.1:5000/flask/add_company/NVDA


kady worker moze byc odpalony z ręki używając w jego folderze komendy:
python3 app.py


łączenie z bazą danych:
psql -h 0.0.0.0 -p 5432 -U postgres

DROP DATABASE sarna WITH (FORCE);
CREATE DATABASE sarna;


a potem wpisanie rzeczy do bazy używając:
2)back (flask) ...back-end-app/main-app$ python3 create_db.py


Wysłanie pliku do backendu:
curl -X POST http://127.0.0.1:5000/flask/upload_data -F "datafile=@/sciezka/do/pliku" -F "modelid=0"


np z flderu ...back-end-app/main-app$ 
curl -X POST http://127.0.0.1:5000/flask/upload_data -F "datafile=@./test.txt" -F "modelid=0"

plik test.txt zawiera poprawne dane

Nowa wersja

Backend po dokeryzacji należy uruchomić w inny sposób

Najlepiej przed próbą uruchomienia *wyczyścić* wszystko:
sudo docker system prune --all --volumes -f

Stworzyć potrzebne workery:
sudo docker build ./basicpredworker/ -t basicpredworker:latest --no-cache
sudo docker build ./stockapiworker/ -t stockapiworker:latest --no-cache
sudo docker build ./main-app/ -t servicedispatcher:latest --no-cache

*Postawić* backend:
sudo docker-compose up

Stworzyć bazę danych:
http://0.0.0.0:5000/make_db/
