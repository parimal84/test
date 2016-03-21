import requests
import math
from datetime import datetime
import datetime as date_time
import json

def convert_date(dt):
    dt = dt[:dt.rindex('0000000+00:00')-1]
    dt_return = datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S')
    return dt_return

# Set the request parameters
records = 0
dups = 0
key = 7448
p_size = 100
pages = 11
status = 'complete'
sort = 'lastupdateddate'
template_id = '2cf0bd2d-f6cb-4034-aebf-a53e01293d36' #post pour template id
t_url = 'https://api.goformz.com/v2/templates/'
f_url = 'https://api.goformz.com/v2/formz/'

temp_url = t_url + template_id + '/formz?' + 'status=' + status
user = 'parimal.shukla@oldcastle.com'
pwd = '0ldC@stle'

# Do the HTTP get request
response = requests.get(temp_url, auth=(user, pwd))

# Check for HTTP codes other than 200
if response.status_code != 200:
    print('Status:', response.status_code, 'Problem with the request. Exiting.')
    exit()

# check total number of records
count = int(response.headers['X-Total-Count'])
total = math.ceil(count/p_size) + 1
print('Total Number of Forms Found', count)

for x in range(39,total):
    template_url = temp_url + '&pagenumber=' + str(x) + '&pagesize=' + str(p_size) + '&sort=' + sort + '%20desc'
    response = requests.get(template_url, auth=(user, pwd))
    data = response.json()  # Decode the JSON response into a dictionary and use the data
    
    #run through each form and get data
    for item in data:
        #skip is John Palma is the User
        
        if item['assignment']['id'] != 'd50ff365-2ea4-4649-8eec-a4d601011b4b' \
            and item['assignment']['id'] != '0d1de4e6-b911-4e0a-be8f-a3ff00e1cb25' \
            and convert_date(item['lastUpdateDate']) < date_time.datetime.now()-date_time.timedelta(days=121):
            key +=1            
            form_url = f_url + item['formId'] + '/exports' #form url
            payload = {'type': 'pdf', 'pages': ''}
            headers = {'content-type': 'application/json'}
            f_response = requests.post(form_url, data=json.dumps(payload), headers=headers, auth=(user, pwd)) #requests GoFormz for data
            q_url = f_response.headers['location'] #link for queue URL
            q_ID = q_url[q_url.index('queue/')+6:] #get export ID from queue url
            link_url = form_url + '/' +q_ID
            l_response = requests.get(link_url, auth=(user, pwd)) #requests GoFormz for data
            l_data = l_response.json()
            
            file = requests.get(l_data['link'], stream=True)
        
            filename = str(key) + '. ' + item['name'] + '.pdf'
            filename = filename.replace('/','-')
            print(filename)

            with open(filename, "wb") as f:
                 f.write(file.content)
                 f.close