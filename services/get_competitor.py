
from api_clients.crunchbase_API import CrunchbaseAPI


class GetCompetitorByKeywords:
    
    def __init__(self,keywords_list, max_num=5):
        self.keywords_list = keywords_list
        self.required_num_of_competitor = max_num
        
    def get_competitors_as_dict_list(self):
        competitors_dict_list =[]#競合他社リストを格納
        crunch = CrunchbaseAPI()
        for keyword in self.keywords_list: #キーワードは、優先度が高いkeywordから要素に格納されている。
            if len(competitors_dict_list)<=self.required_num_of_competitor:
                crunch.search_by_short_description_contains([keyword])
                dict_list = crunch.output_to_dict_list()
                if dict_list:#dict_listが[]の場合がある。
                    competitors_dict_list.extend(dict_list)
        
        competitors_dict_list =competitors_dict_list[:self.required_num_of_competitor]
        return competitors_dict_list
    
    
