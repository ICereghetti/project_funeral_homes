from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import time
import random
from bs4 import BeautifulSoup

# Specify the path to the web driver executable
#driver = webdriver.Chrome("path/to/chromedriver")  # Replace with the actual path to the driver executable

driver = webdriver.Chrome()  # Replace with appropriate web driver

url = "https://funeraldirectors.co.nz/planning-a-funeral/find-a-funeral-director/"  # Replace with the actual website URL
driver.get(url)

final_data=pd.DataFrame(columns=['company','phone','mobile','email','website',
                                 'address','google_map_coord','image_link'])

for j in range(0,19):
    

    table = driver.find_element(By.ID, 'DataTables_Table_0')
    rows = table.find_elements(By.TAG_NAME, 'tr')

    for k in range(0,len(rows[2:])):
        row=rows[2:][k]
        columns = row.find_elements(By.TAG_NAME, 'td')
        
        link = columns[0].find_element(By.TAG_NAME, 'a')
        ActionChains(driver).click(link).perform()
        
        time.sleep(3)
        
        driver.implicitly_wait(3)  # Adjust the waiting time if needed
    
        modal_body = driver.find_element(By.CSS_SELECTOR, '.modal-body')
    
        modal_code=modal_body.get_attribute('outerHTML')
        
        soup = BeautifulSoup(modal_code, 'html.parser')
    
        # Extract the organization name
        organization_name = soup.h1.string.strip()
    
    
    # Extract contact information
        contacts = soup.select('.row > div.col-12')
        contact_data = []
        for i in range(0, len(contacts)-3, 2):
            contact_type = contacts[i].strong.string
            contact_value = contacts[i + 1].get_text(strip=True)
            contact_data.append([contact_type, contact_value])
        address_df = pd.DataFrame(contact_data, columns=['Column', 'Value']).set_index(keys='Column').transpose()
    
    # Extract address
    
        address_lines = []
        for line in soup.address.stripped_strings:
            address_lines.append(line)
        
        address = ', '.join(address_lines)
    
    
    # Extract Google Maps link
        maps_link = soup.find('a', href=lambda href: href and href.startswith('https://www.google.com/maps/search/?api=1'))
        if maps_link:
            maps_link_url = maps_link['href']
            
            maps_link_url_final = maps_link_url.replace('\n', '').replace(' ', '%20')
    
        try: 
            phone=address_df['Phone'][0] 
        except KeyError:
            phone=''
    
        try: 
            mobile=address_df['Mobile'][0] 
        except KeyError:
            mobile=''
    
        try: 
            email=address_df['Email'][0] 
        except KeyError:
            email=''
        try: 
            website=address_df['Website'][0] 
        except KeyError:
            website=''
        
        try: 
            image_link = soup.find('img')['src']
        except Exception:
            image_link=''

    # Create a DataFrame
        data = pd.DataFrame([{'company':organization_name,
                             'phone': phone,
                             'mobile':mobile,
                             'email': email,
                             'website':website,
                             'address':address,
                             'google_map_coord':maps_link_url_final,
                             'image_link':image_link
                             }])
        
        final_data=pd.concat([final_data,data])
        
        # Close the modal
        close_button = driver.find_element(By.CSS_SELECTOR, '.modal-header button.close')
        close_button.click()
        time.sleep(2)
        
        
    next_button = driver.find_element(By.ID, 'DataTables_Table_0_next')
    
    # Click on the "next" button
    next_button.click()
    
    time.sleep(random.randint(5, 10))
    
final_data=final_data.drop_duplicates()

final_data.to_csv('final_data.csv', index=False)




