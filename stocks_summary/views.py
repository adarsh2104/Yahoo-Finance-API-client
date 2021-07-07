from django.shortcuts import render
from django.http import HttpResponse
import requests
from pathlib import Path
from django.conf import settings
from datetime import datetime
from statistics import mean, median ,pstdev, variance


def stocks_info(request):
    if request.method == 'GET':
        path = "market/v2/get-summary"
        querystring = {"region":"US"}

        response = requests.get(url=settings.API_END_POINT+path, headers=settings.HEADERS, params=querystring)
        
        if response.status_code == 200:
            response = response.json()
            response_data = response.get('marketSummaryAndSparkResponse',{}).get('result',[])
            all_stocks_list = parse_response(response_data,keys=['symbol'])

        return render(request,'stocks_summary/stocks_summary.html',{'all_stocks_list':all_stocks_list})

    if request.method == 'POST':
        post_data = dict(request.POST)
        post_data.pop('csrfmiddlewaretoken', None)
        
        requested_data_list = validate_post_data(post_data) 
        requested_stocks_stats = send_data_fetch_request(requested_data_list)

        return render(request,'stocks_summary/requested_stocks_stats.html',{'requested_stocks_stats':requested_stocks_stats})



def send_data_fetch_request(request_data : list):
    path = "stock/v2/get-historical-data"
    
    namewise_stocks_stats = []
    for querystring in request_data:
        
        response = requests.get(url=settings.API_END_POINT+path, headers=settings.HEADERS, params=querystring)
        
        if response.status_code == 200:
            response = response.json()
            
            stocks_stats = {'name':querystring['symbol'],'high':[], 'low':[], 'mean':[], 'median':[],'var':[],'std':[],'datewise_data':[]}
            price_dataset = response.get('prices',[])
            price_dataset = (sorted(price_dataset, key = lambda i: i['date']))

            for datewise_data in price_dataset:
                high = float(datewise_data['high'])
                low = float(datewise_data['low'])
                datewise_data['mean']   = mean([low,high])
                datewise_data['median'] = median([low,high])
                datewise_data['verbose_date'] = datetime.fromtimestamp(int(datewise_data['date'])).strftime('%d-%m-%Y %H:%M:%s')

                stocks_stats['high'].append(high)
                stocks_stats['low'].append(low)
                stocks_stats['mean'].append((high+low)/2)
                stocks_stats['median'].append((high+low)/2)

            stocks_stats['high']     = max(stocks_stats['high'])
            stocks_stats['low']      = min(stocks_stats['low'])
            stocks_stats['mean']     = mean(stocks_stats['mean'])
            stocks_stats['var']      = variance([stocks_stats['low'],stocks_stats['high']])
            stocks_stats['std']      = pstdev([stocks_stats['low'],stocks_stats['high']])
            stocks_stats['median']   = median(stocks_stats['median'])
            stocks_stats['u_bound']  = stocks_stats['mean'] + stocks_stats['std'] 
            stocks_stats['l_bound']  = stocks_stats['mean'] - stocks_stats['std'] 
            stocks_stats['datewise_data'] = price_dataset

            stocks_stats['out_of_bound_count'] = 0
            stocks_stats['first_out_of_bound_ts'] = ''
            stocks_stats['first_return_in_bound_ts'] = ''
            moved_out_of_bound = False
            
            for data in price_dataset:
                if data['low'] < stocks_stats['l_bound'] or data['high'] > stocks_stats['u_bound']:
                    stocks_stats['out_of_bound_count'] += 1
                    if not stocks_stats['first_out_of_bound_ts']:
                        ts = datetime.fromtimestamp(int(data['date'])).strftime('%d-%m-%Y %H:%M:%s')
                        stocks_stats['first_out_of_bound_ts'] = ts
                        moved_out_of_bound = True
                        continue
                
                if moved_out_of_bound and (data['low'] > stocks_stats['l_bound'] or data['high'] < stocks_stats['u_bound']):
                    if not stocks_stats['first_return_in_bound_ts']:
                        ts = datetime.fromtimestamp(int(data['date'])).strftime('%d-%m-%Y %H:%M:%s')
                        stocks_stats['first_return_in_bound_ts'] = ts
        
            namewise_stocks_stats.append(stocks_stats)           
    return namewise_stocks_stats


def parse_response(data_list:list = [],keys:list=[]):
    new_data_list = []
    
    for data in data_list:
        name = data.get(keys[0],False)
        if name:
            data_dict = {'name' : name }
            new_data_list.append(data_dict)
    
    return  new_data_list        


def validate_post_data(post_data:dict = {}):
    requested_data_list = []
    query_keys = post_data.keys()

    for key in query_keys:
        if key.isdigit() and post_data.get(key,''):
            data_dict = {}
            name       = post_data[key+'__'][0].replace('-',' ')
            start_date = post_data[key+'__start_date'][0]
            end_date = post_data[key+'__end_date'][0]
            
            if start_date and end_date:
                epoch_period1 = (datetime.strptime(start_date, "%Y-%m-%d") - datetime(1970, 1, 1)).total_seconds()
                epoch_period2 = (datetime.strptime(end_date, "%Y-%m-%d") - datetime(1970, 1, 1)).total_seconds()
                
                if epoch_period2 - epoch_period1 > 0:
                    data_dict = {'symbol'   : name,
                                'period1'   : int(epoch_period1),
                                'period2'   : int(epoch_period2),
                                "frequency" : "1d",
                                "filter"    : "history"
                                }
                    requested_data_list.append(data_dict)

    return requested_data_list


