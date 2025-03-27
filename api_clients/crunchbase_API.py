import requests
import os
class CrunchbaseAPI:
    
    def __init__(self):
        self.endpoint_url = "https://api.crunchbase.com/v4/data/searches/organizations"
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "X-cb-user-key": os.getenv("CRUNCHBASE_API_KEY")
        }
        self.response = ""

    def search_by_short_description_contains(self,values):
        
        payload = {
            "field_ids": ["permalink", "short_description", "stock_exchange_symbol", "website_url", "uuid", "location_identifiers"],
            "query": [
                {
                    "operator_id": "contains",
                    "type": "predicate",
                    "field_id": "short_description",
                    "values": values
                },
                {
                    "operator_id": "includes",
                    "type": "predicate",
                    "field_id": "location_identifiers",
                    "values": ["Japan"]
                }
            ]
        }
        response = requests.post(self.endpoint_url, json=payload, headers=self.headers)
        self.response = response
        return response

    def output_to_dict_list(self):
        dict_list  =[]
        results = self.response.json()
        for result in results["entities"]:
            dict_list.append({"name":result["properties"]["identifier"]["value"],
                              "short_description":result["properties"].get("short_description","N/A"),
                              "website_url":result["properties"].get("website_url","N/A"),
                              "crunchbase_url":f"https://www.crunchbase.com/organization/{result["properties"]["identifier"]["value"].replace(" ","-").lower()}"
                              })
        
        return dict_list
    
    def display_response(self):
        results = self.response.json()
        print(results["count"])
        print(len(results["entities"]))
        for result in results["entities"]:
            print(result["properties"]["identifier"]["value"],"|",result["properties"]["short_description"],result["properties"].get("website_url","N/A"))
            print()
            
if __name__ == "__main__":
    import sys
    # 現在のスクリプトのディレクトリの親ディレクトリを取得
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from storage.secret_manager import SecretManager
     
    secret_manager = SecretManager()
    
    crunch = CrunchbaseAPI()#Urban mining
    crunch.search_by_short_description_contains(["Crystals"])
    print(crunch.output_to_dict_list())