import requests

from config.config import API_BASE
from utils.logger import logger


def register_user(email, password):
    payload = {
        "firstName": "Test",
        "lastName": "User",
        "userEmail": email,
        "userRole": "customer",
        "occupation": "Scientist",
        "gender": "Male",
        "userMobile": "5678901234",
        "userPassword": password,
        "confirmPassword": password,
        "required": True,
    }

    response = requests.post(f"{API_BASE}auth/register", json=payload, timeout=15)
    logger.info("The user is created with email: %s", email)
    assert response.status_code == 200
