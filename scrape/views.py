# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import re, json, urllib2
import requests
from lxml import html


def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors.
    This function just prints them, but you can
    make it do anything.
    """
    print(e)


def get_response():
    url = "https://www.fincash.com/papi/fund/searchFund"

    querystring = {"am": "Reliance", "q": "", "f": "0", "r": "50", "ag": "0", "se": "", "so": "", "qt": "filter",
                   "bq": "fcpro~tag~2", "pn": "", "dir": "N"}

    headers = {
        'cache-control': "no-cache",
        'postman-token': "693fbc1c-397c-dae0-0af4-6a9e32fd46f6"
    }
    resp = []
    response = requests.request("GET", url, headers=headers, params=querystring)
    query_data = response.json()
    for d in query_data['funds']:
        vals = d['basicFactsheet']
        print vals
        name = vals['name'].lower().replace(" ","-")
        resp.append({"fund_name": vals['name'], "1Y": round(float(vals['ret1yr']), 2),
                     "3Y": round(float(vals["ret3yr"]), 2),
                     "url": "https://www.fincash.com/factsheet/{name};am=Reliance;q=;f=0;r=10;ag=0;ra=;c=;sc=;se=;so=;ar=;o=;qt=filter;bq=fcpro~tag~2;nq=;pn=;fo=;dir=N;fid={id}".format(name=name, id=vals['id'])})
    # raw_html = simple_get('https://www.fincash.com/explore;am=Reliance;q=;f=0;r=50;ag=0;ra=;c=;sc=;se=;so=;ar=;o=;qt=page;bq=fcpro~tag~2;nq=;pn=;fo=;dir=N')
    # html = BeautifulSoup(raw_html, 'html.parser')
    # for a in html.findAll("a", attrs={'class':'verdana12blue'}):
    #     print a['href']
    # for a in html.select('mat-card'):
    #     for d in a.select("div"):
    #         if len(d.select('a')) > 0:
    #             url = d.select('a')[0]['href']
    #         if a.text.startswith(" Reliance") and re.search("%", a.text):
    #             val = str(re.sub(r"[^a-zA-Z0-9 -.%]+", ' ', a.text.splitlines()[0])).strip()
    #             try:
    #                 val_split = val.split("  ")
    #                 mf_name = val_split[0]
    #                 per_cur = val_split[1].index("%")
    #                 per_next = val_split[1].index("%", per_cur+1)
    #                 data = val_split[1]
    #                 per_first = data[:3]
    #
    #                 per_sec = data[per_cur+1:per_next]
    #                 response.append({"fund_name": mf_name, "1Y": float(per_first), "3Y": float(per_sec), "url": "https://www.fincash.com"+url})
    #             except Exception:
    #
    #                 val_split = re.split(r"Not Rated| Not Rated-", val)
    #                 mf_name = val_split[0]
    #                 per_cur = val_split[1].index("%")
    #                 per_next = val_split[1].index("%", per_cur + 1)
    #                 data = val_split[1]
    #                 per_first = data[:3]
    #                 per_sec = data[per_cur + 1:per_next]
    #                 response.append({"fund_name": mf_name, "1Y": float(per_first), "3Y": float(per_sec),
    #                                  "url": "https://www.fincash.com" + url})
    #     # [dict(t) for t in {tuple(d.items()) for d in l}]
    # response = [dict(t) for t in {tuple(d.items()) for d in response}]
    return resp


def get_response_2():
    raw_html = urllib2.urlopen('https://mutualfund.wishfin.com/reliance-mutual-fund').read()
    html = BeautifulSoup(raw_html, 'html.parser')
    response = []
    for a in html.select('li'):
        data = dict()
        link = a.select("a")

        if len(link) > 0:
            link = link[0]
            try:
                if 'reliance' in link['href']:
                    data['url'] = link['href']
                    data['fund_name']=link.text
            except Exception:
                pass
        percent = a.select("li")
        if len(percent) > 1:
            percent = percent[1]
            span = percent.select("span")
            if len(span) > 1:
                data["1Y"] = float(span[1].text.split(" ")[0])
                data["3Y"] = 0
            else:
                print "NA"
        if len(data) > 0:
            response.append(data)
    response.pop(-1)
    return response


def get_response_wealth_trust():
    url = "https://wealthtrust.in/api/api/GetSearchResultForFundExplorer"

    payload = json.dumps({"Data_Size": 800,"Fund_Name": [],"Horizon": [],"Plan_Opt": [],"Plan_Type": [],"Rating": [],"Risk": [],"Sorting_ParamsId": [0],"0": 0,"Start_No": 0,"objCategorySubCategory": [],"search_text": "reliance"})
    headers = {
        'token': "6847d2bc-7a2e-4bd4-897f-3cdf4fa7a1a3",
        'cache-control': "no-cache",
        'content-type': "application/json",
    }

    response = requests.request("POST", url, data=payload, headers=headers)
    resp = []
    data = response.json()
    for d in data['WAPIResponse']:
        resp.append({"fund_name": d['Plan_Name'], "1Y": round(d['Returns_1Yr'],2), "3Y": round(d["Returns_3Yr"],2),
                     "url": "https://wealthtrust.in/en/fund-detail/"+ str(d["LinkPlanName"]) + "/" + str(d["scheme_mapping_Id"])})

    # response = requests.get('https://wealthtrust.in/en/fund-explorer')
    # tree = html.fromstring(response.text)
    # data = tree.xpath(".//div[@class='feBox']")
    # response = []
    # for d in data:
    #     # if "Reliance" in d.text_content().split("\n"):
    #     val = d.text_content().split("\n")
    #     resp = [x.strip() for x in val if x.strip() != ""]
    #     fund_name = resp[0]
    #     url = "https://wealthtrust.in" + d.xpath(".//a")[0].xpath("@href")[0]
    #     percent = resp[resp.index("3Y") + 1].split("%")[0]
    #     response.append({"fund_name": fund_name,"3Y":percent, "url": url} )
    # return response

    return resp


def clear_funds():
    url = "https://www.clearfunds.com/mutual-fund-explorer.json"
    query_data = []
    for i in range(1,14):
        querystring = {"growth": "true", "fund_family[]": "Reliance", "order": "", "sortColumn": "3y", "div_r": "true",
                       "div_p": "true", "page": i}

        headers = {
            'cache-control': "no-cache",
            'postman-token': "9ae07556-b666-1ae9-46f8-87f53684e980"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)
        data = response.json()

        query_data.extend(data['funds'])
    resp = []
    query_data = [dict(t) for t in {tuple(d.items()) for d in query_data}]
    for d in query_data:
        resp.append({"fund_name": d['fund_name'], "1Y": round(float(d['returns_1_year']), 2), "3Y": round(float(d["returns_3_years"]), 2),
                     "url": str(d["url"])})

    # response = requests.get("https://www.moneycontrol.com/india/mutualfunds/mutualfundsinfo/snapshot/R")
    # tree = html.fromstring(response.text)
    # base_url = "https://www.moneycontrol.com"
    # links = tree.xpath("//a[@class='verdana12blue']")[:50]
    # responses = []
    # for l in links:
    #     url = base_url + l.xpath("@href")[0]
    #     fund_name = l.text
    #     next_page = html.fromstring(requests.get(url).text)
    #     dat = next_page.xpath("//div[@class='col-350 FL']")[0].xpath(".//table")[0].xpath(".//tr")[1:]
    #     per_list = []
    #     for r in dat:
    #         val = r.text_content().strip()
    #         val = [a.replace('\t', "") for a in val.split("\n")]
    #         if "1 Year" in val or '3 Years' in val:
    #             per_list.append(val[1])
    #     responses.append({"fund_name": fund_name, "1Y":per_list[0], "3Y": per_list[1],"url":url })

    return resp


def paisa_bazaar():
    url = "https://mfapi.paisabazaar.com/api/Scheme/GetAllFundListEquityDirect"
    url_2 = "https://mfapi.paisabazaar.com/api/Scheme/GetAllFundListGrowthDirect"
    headers = {
        'cache-control': "no-cache",
        'postman-token': "04bb14f3-c897-7816-9364-f37354007be5"
    }

    response = requests.request("POST", url, headers=headers)
    response_2 = requests.request("POST", url_2, headers=headers)
    resp = []
    data = response.json()
    data_2 = response_2.json()

    query_data = []
    query_data.extend(data["ReturnData"])
    query_data.extend(data_2["ReturnData"])
    for d in query_data:
        if "Reliance" in d['NameOfScheme']:
            resp.append({"fund_name": d['NameOfScheme'], "1Y": round(float(d['R1Year']), 2), "3Y": round(float(d["R3Year"]), 2),
                     "url": "https://mutualfund.paisabazaar.com/funds-explorer#/buy/" + str(d["NameOfSchemeForUrl"])})

    return resp


def clear_tax():

    url = "https://rix9bss5j6-dsn.algolia.net/1/indexes/clearsave_mutual_funds/query"

    querystring = {"x-algolia-agent": "Algolia for vanilla JavaScript 3.30.0", "x-algolia-application-id": "RIX9BSS5J6",
                   "x-algolia-api-key": "353ac0c803e6c9cd775236eb90e28c6d"}

    payload = "{\"params\":\"query=reliance&page=0&hitsPerPage=100&facetFilters=%5B%5B%5D%5D\"}\n"
    headers = {
        'content-type': "application/json",
        'referer': "https://cleartax.in/save/search?ref=homepage-cta-save&filters=%7B%22query%22%3A%22reliance%22%7D",
        'origin': "https://cleartax.in",
        'cache-control': "no-cache",
        'postman-token': "2770368a-6da7-86eb-30bb-24d8311285cd"
    }

    response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
    data = response.json()
    resp = []

    for r in data['hits']:
        values = r['fundMetaData']
        resp.append({
            "fund_name":values['fundLegalName'],
            "1Y": values['returns']['return1yr'],
            "3Y": values['returns']['return3yr'],
            "url": "https://cleartax.in/mf/reliance/{}/{}".format(values['slug'], values['isinCode'])
        })

    return resp


def upwardly():
    url = "https://www.upwardly.in/api/v1/search"

    payload = "{\"from\":0,\"size\":200,\"filter\":{\"amc\":[\"Reliance\"]},\"q\":\"all funds\"}\n"
    headers = {
        'content-type': "application/json",
        'cache-control': "no-cache",
        'postman-token': "a113393a-51bc-9e4e-e606-aae337178d00"
    }

    response = requests.request("POST", url, data=payload, headers=headers)
    data = response.json()
    resp = []

    for r in data['results']:
        values = r['_source']
        if values['return1y'] and values['return3y']:
            resp.append({
                "fund_name": values['name'],
                "1Y": round(float(values['return1y']),2),
                "3Y": round(float(values['return3y']),2),
                "url": "https://www.upwardly.in/en/mutual-fund/{}".format(values['slug'])
            })
        
    return resp


@csrf_exempt
def home(request):
    if request.method == "GET":
        return render(request, "home.html")
    else:
        val = request.POST.get("home", "")
        if val == "fin_cash":
            data = get_response()
        elif val == "wishfin":
            data = get_response_2()
        elif val == "wealth":
            data = get_response_wealth_trust()
        elif val == "clear":
            data = clear_funds()
        elif val == "paisa":
            data = paisa_bazaar()
        elif val == 'ctax':
            data = clear_tax()
        else:
            data = upwardly()

        return render(request, "result.html", {"data": data})
        # return HttpResponse(json.dumps(data))

