####################################### SETUP ###################################


import requests
from bs4 import BeautifulSoup
import re
import json
import pandas as pd
import time
from tqdm import tqdm
from urllib.parse import urlparse
from collections import Counter
import openai
import os

### FUNCTION TO SCRAPE USING BS4

def scrape_page(url):
    response = requests.get(url,headers={'User-Agent':'Mozilla/5.0'})
    html_content = response.content

    soup = BeautifulSoup(html_content, "html.parser")

    return soup

### FUNCTION TO CLEAN TEXT

def clean_text(text):
    # Remove excessive whitespace
    text = re.sub(r'\n\s*\n', '\n', text.strip(), flags=re.MULTILINE)
       
    # Use concise language
    text = re.sub(r'\n\s+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

### FUNCTION TO USE CHAT GPT RETRYING AFTER AN ERROR

def get_completion_2(prompt, model="gpt-3.5-turbo",):
    max_attempts = 20
    retry_delay = 5
    for j in range(max_attempts):
        try:
            messages = [{"role": "user", "content": prompt}]
            response_request = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=0, # this is the degree of randomness of the model's output
            )
            response=response_request.choices[0].message["content"]
            time.sleep(20)
            break
    
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Retrying...")
            time.sleep(retry_delay)
    return response

### FUNCTION TO LOOK FOR COMMON PREFIX


def find_common_prefix(strings):
    if not strings:
        return ""
    
    shortest_string = min(strings, key=len)
    prefix = ""
    
    for i, char in enumerate(shortest_string):
        if all(string[i] == char for string in strings):
            prefix += char
        else:
            break
    
    return prefix 

### FUNCTION TO REMOVE BS4 TITLES

def remove_titles(strings):
    cleaned_strings = []
    for string in strings:
        if string.find(' - ') != -1 and string.find(' - ') < 40:
            cleaned_strings.append(string[string.find(' - ') + 3:])
        else:
            cleaned_strings.append(string)
    return cleaned_strings

### FUNCTION TO REMOVE COMMON PREFIX

def common_prefix(strings):
    strings_clean=remove_titles(strings)
    # Find the common prefix length
    prefix = os.path.commonprefix(strings_clean)
    
    return prefix

### FUNCTION TO REMOVE BS4 SUFFIX

def common_suffix(strings):
    strings_clean=remove_titles(strings)
    # Find the common suffix length
    suffix = os.path.commonprefix([s[::-1] for s in strings_clean])[::-1]
    return suffix


### FUNCTION TO REMOVE PREFFIX AND SUFFIX

def remove_substring_if_present(strings, substring):
    modified_strings = []
    for string in strings:
        if substring in string:
            modified_string = string.replace(substring, "")
            modified_strings.append(modified_string)
        else:
            modified_strings.append(string)
    return modified_strings

### FUNCTION TO SPLIT STRINGS INTO TOKENS

def split_strings(strings):
    MAX_TOKENS = 3500
    split_strings = []
    
    for string in strings:
        tokens = string.split()  # Split string into individual tokens
        parts = []
        current_part = ""
        
        for token in tokens:
            current_part += token + " "
            if len(current_part) >= MAX_TOKENS:
                # Check if the current part ends with a sentence-ending punctuation
                if current_part.rstrip().endswith(('.', '!', '?')):
                    parts.append(current_part.strip())
                    current_part = ""
                else:
                    # Find the last sentence-ending punctuation in the current part
                    last_punctuation_index = max(
                        current_part.rfind('.'),
                        current_part.rfind('!'),
                        current_part.rfind('?')
                    )
                    
                    # Split the current part at the last sentence-ending punctuation
                    parts.append(current_part[:last_punctuation_index + 1].strip())
                    current_part = current_part[last_punctuation_index + 1:].strip()
        
        if current_part:
            parts.append(current_part.strip())
        
        split_strings.extend(parts)
    
    return split_strings  

### FUNCTION TO FILTER TEXT FROM A JSON LIST


def filter_json_strings(strings):
    json_strings = []
    
    for string in strings:
        try:
            json_object = json.loads(string)
            json_strings.append(string)
        except ValueError:
            # Ignore if it's not a valid JSON
            pass
    
    return json_strings



################################ CODE ###############################

### CHOOSE AND CLEAN 8 WEBSITES TO SCRAPE

websites = [
    'www.asimplecremation.co.nz',
    'https://academyfunerals.co.nz/',
    'https://www.affinityfunerals.nz/',
    'http://www.affinityfunerals.nz/',
    'https://croftfunerals.co.nz/',
    'https://affordablefunerals.co.nz/',
    'https://www.ana-maria.nz/',
    'https://www.aorakifuneralservices.info/'
]

updated_websites = []


for website in websites:
    if not website.startswith('http'):
        website = 'http://' + website
    updated_websites.append(website)

final_answers=[]

############################## LOOP TO SCRAPE EACH ONE OF THEM ############

for m in tqdm(range(len(updated_websites))):
    
########################## WE GET ALL THE TEXT OF ALL PAGES OF THE SITE INTO A LIST TO SCRAPE ###################

    url = updated_websites[m]
    base_url_original=urlparse(url).netloc
    soup = scrape_page(url)    
    title = soup.title.text    
    page_links = soup.find_all("a")    
    page_links_clean=[page.get("href") for page in page_links]
    
    data_collection = []

    for link in tqdm(page_links):
        page_url = link.get("href")
        try:
            base_page_url= urlparse(page_url).netloc
            if base_page_url=='':
               if url.endswith('/'):
                   page_url = url.rstrip('/')+page_url
               else:
                   page_url = url+page_url
               base_page_url= urlparse(page_url).netloc
        except Exception as e:
            base_page_url=''
        if page_url and base_url_original==base_page_url and not (page_url.endswith(".pdf") or page_url.endswith(".jpg")):
            page_soup = scrape_page(page_url)
    
            title = page_soup.title.text
            page_text = clean_text(page_soup.get_text())
            page_code = page_soup.prettify()
            
            data_collection.append([title,page_text,page_url,page_code])
    
    unique_list = [list(sublist) for sublist in set(tuple(sublist) for sublist in data_collection)]
    
    text_to_process=[l[1] for l in unique_list]
    
################################# WE THEN REMOVE PREFIX AND SUFIXES TO AVVOID REPETITIVE TEXT
    
    prefix=common_prefix(text_to_process)
    
    suffix=common_suffix(text_to_process)

    text_to_process_final=remove_substring_if_present(remove_substring_if_present(text_to_process
                                                      ,prefix),suffix)
    
    text_to_process_final.append(prefix)
    text_to_process_final.append(suffix)
    
################################# WE USE CHAT GPT TO CLEAN THE TEXT 
   
    openai.api_key = [API_KEY]
    
    text_to_process_final_splitted=split_strings(text_to_process_final)

    clean_samples=[]
    
    for i in tqdm(range(0,len(text_to_process_final_splitted))):
        
        text_to_clean=text_to_process_final_splitted[i]
        prompt= f"""I got this text from a bs4 element, in Python. I'm scraping Funeral company's information.
        Could you please make it pretty without loosing any relevat information about the business?
        '''{text_to_clean}'''
        """
        response = get_completion_2(prompt)
        
        clean_samples.append([response]) 
    
    
    answers=[]
    
##################### WE THEN ASK CHAT GPT TO SCRAPE SPECIFIC FIELDS THAT OUR CLIENT WANTED TO HAVE I HIS DB
    
    for i in tqdm(range(0,len(clean_samples))):
        text=clean_samples[i]
            
        prompt = f"""
                    I got a series of text, scraped from website with bs4.  
                    Could you please add the correct answer of field list as a json. Each iteration is going to add more information, so update the json response in order to reflect all data. \ 
                    If the information is not in the text, put 'unknown' as a result. \
                    Json list fields to create and complete:
                    1) company_name: What is the name of the business?
                    2) company_address: What is the company address?
                    3) company_phones: Python's list of phones
                    4) company_mails: Python's list of mails.
                    5) company_social_media: Python's list of social media profiles
                    6) services: Give me a json formatted text describing their services with the next fields: name (name of the service), type (the type of service it is: Cremation, Funeral, etc. Choose a word that exaplains what the service offers), price and description (a maximun 15 word descripttion about what the service includes)
                    7) specializations: If a funeral home or service provider has specific areas of expertise or caters to certain religious or cultural practices, these details are mentioned.
                    8) payment_options: Information on accepted payment methods, such as credit cards, checks, or financing options, may be included.
                    9) licenses_and_certifications: Python's list of licenses, certifications or affiliations held by the funeral home or service provider, ensuring that they meet professional standards.
                    10) staff_information: Full Name and position in company.
                    11) languages_spoken: If the funeral home staff can provide services in languages other than English, this could be an important consideration for some users.
                    12) additional_services: Beyond the basic funeral services, some funeral homes might offer additional services like grief counselling, estate planning, or funeral webcasting, caskets, preplanning, etc. Make a Python list of the names of those services.
                    13) covid19_safety_measures: Given the current pandemic situation, it might be helpful to users to know what safety measures the funeral home is taking, like requiring masks, limiting the number of attendees, etc.
                    14) ownership = This indicates if it's owned by a foreign company, locally owned, a co-opperative, a chain, etc.
                    15) reviews_list:  If they have client's reviews in their website, I need a Python's list of review's text, who made it and the rating.
                    16) facilities: Information about venues and facilities for the funeral with the next structure:  "facility name (capacity formatted as a number if avaliable).
                    17) location: Include the funeral home's location, such as the city or neighborhood it is in.
                    18) availability: To know if the funeral home is available 24/7, has specific hours of operation, or offers immediate services.
                    19) transportation: If the funeral home offers transportation services, such as a hearse or limousine.
                    20) sustainability: Some funeral homes offer eco-friendly or sustainable options, such as biodegradable caskets or green burial services
                    
                    The scraped text is the following:
                    ```{text}```
                    """
        response = get_completion_2(prompt)
    
        answers.append(response)
    
######################### WE THEN MIX ALL ANSWERS INTO ONE, FOLLOWING DIFERENT INSTRUCTIONS FOR EACH FIELD

    
    answers_data = [json.loads(json_string) for json_string in filter_json_strings(answers)]
    
    df = pd.DataFrame(answers_data)
    
    
    columns = df.columns.tolist()
    
    how_to=[['company_name','I need you to grab the most common name'],
     ['company_address','I need you to get the most complete address'],
     ['company_phones','I need you toget all unique phones as a Python list'],
     ['company_mails','I need you to get all unique mails as a Python list'],
     ['company_social_media','I need you to get all unique mails as a Python list'],
     ['services','I need you to list item for each service with the columns name, type, price and description. You can check the same services in the multiple options in order to complete each one. The price needs to be a number only. Ensure that your JSON file is syntactically correct.'],
     ['specializations','I need you to get all unique specializations as a Python list'],
     ['payment_options','I need you to get all unique specializations as a Python list'],
     ['licenses_and_certifications','I need you to get all unique values as a Python list'],
     ['staff_information','I need you to get all different values from the staff as a Python list. You can check the same people in the multiple options in order to complete all fields'],
     ['languages_spoken','I need you to get all unique values provided as a Python list. Ignore the unknown values or empty lists'],
     ['additional_services','I need you to get all different values from the additional services as a Python list'],
     ['covid19_safety_measures','I need you to get all answers into one. Ignore the unknown values'],
     ['ownership','I need you to get all answers into one to explain the type of ownership. Ignore the unknown values'],
     ['reviews_list','I need you to get each review with their fields as a Python list. If there are no reviews, give me a empty json'],
     ['facilities','I need you to get all different facilities as a Python list. You can check the same facilities in the multiple options in order to complete each one'],
     ['location','I need you to grab the most common location in the format "City, State". Ignore the unknown values'],
     ['availability','I need you to get all answers into one. Ignore the unknown values'],
     ['transportation','I need you to get all answers into one. Ignore the unknown values'],
     ['sustainability','I need you to get all answers into one. Ignore the unknown values']]
    
    
    how_to_df=pd.DataFrame(how_to,columns=['columna','how']).set_index('columna')
    
    merged_dict={}
    
    for i in tqdm(range(len(df.columns))):

        columna=df.columns[i]
        how_to_process=how_to_df.loc[columna][0]
        columna_valores=list(df[columna])
    
        columna_valores = [str(sublist) for sublist in columna_valores]
    
        frequency_counter = Counter(columna_valores)
        
        
        limite=len(str(frequency_counter).split())+len(how_to_process.split())+103        

        token_left=4080-limite        

        prompt = f"""
                I have this list of possible values for a string. \
                Each option is a different answer given by an AI. The numbers are how frequent each option is. \
                Could you please create one answer for this field? If all options are empty or unknown, answer it with 'unknown' \
                Ignore unknown values and empty lists. Do not generate the values based on other criteria than the list.
                The criteria to create the answer is the following:
                    '''{how_to_process}'''
                Structure your answer as a valid json object, with a field named '''{columna}'''. \
                
                The frequency is the following: \
                ```{frequency_counter}``` \
    
                """

        
        response = get_completion_2(prompt)
        try:
            json_dict = json.loads(response)
        except Exception as e:
            json_dict = json.loads('{"'+columna+'": ""}')
        merged_dict.update(json_dict)
    
    #### WE MIX EVERYTHING INTO ONE JSON TO HAVE OUR ANSWER
    
    final_answers.append(merged_dict)
    
    final_answers_filtered=[d for d in final_answers if d]
    
    output_file = 'samples.json'

    # Save the list of dictionaries as a JSON file
    with open(output_file, 'w') as file:
        json.dump(final_answers_filtered, file)
