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


def test():
    add_product("PSINA", 179, "Test psina item", "This is the best test psina item to buy", 123, 1.81,
                ["test", "psina", "item"])

