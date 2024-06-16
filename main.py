import requests
# from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import csv

# URL of the form submission endpoint
url = 'https://lifesincerity.com/checkmark/action.php'  # Replace with your actual endpoint

# Array of student IDs to be tested
student_ids = ['D5393', 'D5398', 'D5409', 'D5663', 'D5453', 'D5457', 'D5676', 'D5655', 'D5487', 'D5495', 'D5504', 'D5517', 'D5521', 'D5556', 'D5564', 'D5574', 'D5576', 'D5583', 'D5368', 'D5732', 'D5632', 'D5385', 'D5706', 'D5635']
retries = []

# List to store the extracted data
data_extracted = {}


def extract_and_store_data(response_text, id):
    soup = BeautifulSoup(response_text, 'html.parser')
    tables = soup.find_all('table')
    results = []

    for table in tables:
        rows = table.find_all('tr')
        result = {}
        for row in rows:
            cols = row.find_all('td')
            result[cols[0].get_text()] = cols[1].get_text()
        results.append(result)
    data_extracted[id] = results;


def send_post_request(student_id):
    dt = {'school_id': student_id}
    try:
        response = requests.post(url, data=dt)
        if response.status_code == 200:
            # print(response.text)
            extract_and_store_data(response.text, student_id)
        else:
            print(f'Student ID: {student_id}, Status Code: {response.status_code}')
            retries.append(student_id)  # Retry the request later
    except requests.exceptions.RequestException as e:
        print(f'Student ID: {student_id}, Error: {e}')
        retries.append(student_id)


# Use ThreadPoolExecutor to send requests in parallel
# with ThreadPoolExecutor(max_workers=1) as executor:
#     executor.map(send_post_request, student_ids)

for id in student_ids:
    send_post_request(id)

while(len(retries) > 0):
    send_post_request(retries.pop())

# Save all data into csv file
flattened_data = []

for id, records in data_extracted.items():
    add = []
    add.append(id)
    for record in records:
        for key, value in record.items():
            add.append(value)
    flattened_data.append(add)

headers = ["Student ID", "MM Paper 1", "MM Paper 2", "Sikap MM", "Total MM", "AM Paper 1", "AM Paper 2", "Sikap AM", "Total AM"]

with open('data.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(headers)
    writer.writerows(flattened_data)