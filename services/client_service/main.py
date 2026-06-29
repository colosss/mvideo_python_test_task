from src.config.settings import settings
from src.interfaces.worker import run_client_service

if __name__=="__main__":
    run_client_service(settings)