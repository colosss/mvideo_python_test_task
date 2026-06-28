from src.config.settings import settings
from src.interfaces.scheduler import run_background_service

if __name__=="__main__":
    run_background_service(settings)