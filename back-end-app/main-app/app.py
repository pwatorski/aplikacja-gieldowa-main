from werkzeug.middleware.dispatcher import DispatcherMiddleware
from service_companies import app as company_data_service
from service_file_upload import app as file_upload_service
from service_user_pred import app as own_prediction_service
from base_app import app as base_app

application = DispatcherMiddleware(base_app, {
    '/upload': file_upload_service,
    '/user_pred':own_prediction_service,
    '/company': company_data_service
})