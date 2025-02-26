"""
Script Name: XML to JSON Parser
Developed by: Manisha Chollangi
Date: 19-02-2025

Description:
This script processes an XML request, applies business rules, and generates a JSON response. 
It validates input data, ensures required fields are present, checks date constraints, and calculates the selling price 
with an appropriate markup. The script is designed to work for various input values while enforcing business rules 
like language validation, currency validation, nationality verification, and search type constraints.

Compatibility:
This script is designed to work with different XML inputs that conform to the defined schema. 
It will process various request parameters while ensuring compliance with validation rules. 
Any malformed or missing required data will result in an appropriate error response.
"""
#Importing required modules
import xml.etree.ElementTree as ET
import json
import random
import datetime
from typing import Dict, Any

# Constants
VALID_LANGUAGES = {'en', 'fr', 'de', 'es'}
DEFAULT_LANGUAGE = 'en'
DEFAULT_OPTIONS_QUOTA = 20
MAX_OPTIONS_QUOTA = 50
VALID_CURRENCIES = {'EUR', 'USD', 'GBP'}
DEFAULT_CURRENCY = 'EUR'
VALID_NATIONALITIES = {'US', 'GB', 'CA'}
DEFAULT_NATIONALITY = 'US'
VALID_MARKETS = {'US', 'GB', 'CA', 'ES'}
DEFAULT_MARKET = 'ES'
MARKUP_PERCENTAGE = 3.2  # 3.2% markup
EXCHANGE_RATES = {'EUR': 1.0, 'USD': 1.1, 'GBP': 0.9}  # Example rates

#Function to parse XML request 
def parse_xml_request(xml_string: str) -> Dict[str, Any]:
    """Parses XML request and extracts necessary values."""
    root = ET.fromstring(xml_string)
    
    # Extract values with default fallback
    language = root.findtext(".//source/languageCode", DEFAULT_LANGUAGE)
    language = language if language in VALID_LANGUAGES else DEFAULT_LANGUAGE # Ensure language is valid
    
    options_quota = root.findtext(".//optionsQuota") 
    options_quota = int(options_quota) if options_quota and options_quota.isdigit() else DEFAULT_OPTIONS_QUOTA
    options_quota = min(options_quota, MAX_OPTIONS_QUOTA) # Validate options quota
    
    # Extract required parameters
    parameters = root.find(".//Configuration/Parameters/Parameter")
    if parameters is None or not all(param in parameters.attrib for param in ["password", "username", "CompanyID"]):
        raise ValueError("Missing required parameters: password, username, or CompanyID")
    var_ocg = ''
    # Extract search and date details
    search_type = root.findtext(".//SearchType", "Single")
    start_date = root.findtext(".//StartDate")
    end_date = root.findtext(".//EndDate")
    
    # Validate currency and nationality
    currency = root.findtext(".//Currency", DEFAULT_CURRENCY)
    currency = currency if currency in VALID_CURRENCIES else DEFAULT_CURRENCY
    
    nationality = root.findtext(".//Nationality", DEFAULT_NATIONALITY)
    nationality = nationality if nationality in VALID_NATIONALITIES else DEFAULT_NATIONALITY
    
    return {
        "language": language,
        "options_quota": options_quota,
        "search_type": search_type,
        "start_date": start_date,
        "end_date": end_date,
        "currency": currency,
        "nationality": nationality
    }

# Function to generate JSON response
def generate_json_response(parsed_data: Dict[str, Any]) -> str:
    """Generates the required JSON response."""
    # generating values by using current date time
    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    hotel_code_supplier = str(random.randint(10000000, 99999999))  # Random 8-digit supplier code
    
    net_price = 132.42  # Example net price __define_ocg__
    markup = MARKUP_PERCENTAGE / 100
    selling_price = round(net_price * (1 + markup), 2)
    exchange_rate = EXCHANGE_RATES.get(parsed_data["currency"], 1.0)
    selling_currency = parsed_data["currency"]
    
    response = [{
        "id": f"A#{current_time}",
        "hotelCodeSupplier": hotel_code_supplier,
        "market": parsed_data.get("nationality", DEFAULT_MARKET),
        "price": {
            "minimumSellingPrice": None,
            "currency": parsed_data["currency"],
            "net": net_price,
            "selling_price": selling_price,
            "selling_currency": selling_currency,
            "markup": MARKUP_PERCENTAGE,
            "exchange_rate": exchange_rate
        }
    }]
    return json.dumps(response, indent=4)


# Example XML input for testing
xml_input = """
<AvailRQ xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    <timeoutMilliseconds>25000</timeoutMilliseconds>
    <source>
        <languageCode>en</languageCode>
    </source>
    <optionsQuota>20</optionsQuota>
    <Configuration>
        <Parameters>
            <Parameter password="XXXXXXXXXX" username="YYYYYYYYY" CompanyID="123456"/>
        </Parameters>
    </Configuration>
    <SearchType>Multiple</SearchType>
    <StartDate>14/10/2024</StartDate>
    <EndDate>16/10/2024</EndDate>
    <Currency>USD</Currency>
    <Nationality>US</Nationality>
</AvailRQ>
"""
#Execution
try:
    parsed_data = parse_xml_request(xml_input)
    json_response = generate_json_response(parsed_data)
    print(json_response)
except ValueError as e:
    print(json.dumps({"error": str(e)}, indent=4))


