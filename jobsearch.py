import requests
import creds

class jobError(Exception):
     def __init__(self, statusCode, errorMessage):
          self.statusCode = statusCode
          self.errorMessage = errorMessage
          super().__init__(self.errorMessage)

     def __str__(self):
          return f"Error Code {self.statusCode}: \n{self.errorMessage}"


class jSearch():
     def getJobs():
          url = "https://jsearch.p.rapidapi.com/search"

     ## hard coded in decide on if the query should be changed via discord messages
          querystring = {
               "query":"software engineering jobs in georgia","page":"1","num_pages":"1","country":"us","date_posted":"week","employment_types":"FULLTIME,INTERN"
          }

          headers = {
               creds.api_key
          }

          response = requests.get(url, headers=headers, params=querystring)
          if response.status_code == 200:
               return response.json()
          else:
               raise jobError(response.status_code, response.text)
     


