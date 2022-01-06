import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import json
import os
from dotenv import dotenv_values
config = dotenv_values(".env")
from images import Keyword, Product, ProductKeyword
from SessionManager import SessionManager
from add_product import add_product
from keywords import get_keywords

# print(get_keywords("""Example texts include those emanating from such international organizations as the International Chamber of Commerce, the regional accreditation bodies operating under the aegis of the International Organization for Standardization, the World Wide Web Consortium, as well as the work of UNCITRAL itself."""))


def test():
    add_product("PSINA", 179, "Test psina item", "This is the best test psina item to buy", 123, 1.81,
                ["test", "psina", "item"])

