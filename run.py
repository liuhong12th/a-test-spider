import re
import requests
import datetime
from html.parser import HTMLParser


def send_request(date):
    payload = {
        "__VIEWSTATE": "P2ZnLXLxL3WnWcxlj36WgjzqorXFoSvxwK/QOsfewmAfqwA+MzYp1UX1GSkgqdhBU08J6tip21K1WvTliz4X/JtWCRQdgKPZ8QlHe8ie5MZACcD0i4Ty07avdmuMCt2yj4BncolVyKiOzuNBeMK23nDZDzHYLhRdgfAnedkrHqx5ZKvj3SbrBmII/KBvPALhtExZIw==",
        "__VIEWSTATEGENERATOR": "EC4ACD6F",
        "__EVENTVALIDATION": "TqfsE8Df/prFsl62aIWrEUIz4WmpID540c0seTZTskW9o1q0svKUrXXCsMOwBJZDiHciNSeZ7PuLXcDjgeagM92DscW8Y4ZaaWYspXmi1yEQuq6/+Bf4Dx4bD6ePq/j2KrLev9G36zSPVe5oa05W77JJz28kbWvZqLsqlW0bf4ienYf6Gy1DKxgoJInR8Fs3Scd6Yw2bSC/7f1MVJca1L+G3/yThWpsmJ79aHfK/f0HQmT/3waUDGxckIBfItDu+iOg314gHj5tuiP1qeypXve4C+Cp/jDxq9bCU+Z7VgKxSllXfjQzOkIPjjPM3oCy1hu/kvZdZD0Nmz5pOoP9DRFdOcgtXiue5f5uohwwDxbiKN3OljYPy4xPhPV35wTrvyUrZo5oLd0s8lWsgyrdBxo3STffS8zgMjh3vfKLgGXGUBL+Z27EmwQBB+Gj+uENmV/YInWceA8kqKSTiBptT7xhEjpmCaJcUFADpEO3KUDtmhEv4+gZ80jF3pzJ4oCwK33GMMfypAfJs1ZwUvh223g3pTdaViOs1MtO9wA5fHy8W+NFKcL+/O+IfWVTmg8Vt1bs2kSphxwXCFIazPNB8y/6CBiJO3MUfaHK154V7xd3QP+sQtFYR2p+IVMop1+IqfgD+ePpOx8OR0Uly898ba8h0SN3RxHRmt2Man+ZfeU4Cti6xF011+C/IP6s0ojWeUsVJgGl/8+Rz3Jd2Vu4ureTTivxwUer62GULMhtHch7oCztPWVvQJewWUShQS13OlJmAUZKaG4g6/GhCFgNGYfEynVUbQ5KzZ36+ynoAngt240tdo48HxUUosH4fVXR8wJ7Yz1EJUy7zJwIA7zcy3MKxIDRsbfZiuIncNC6+8sO5U9dz4rYmSsbYIJg/pUk5Crt4ncfCSehRpWQ63mxDv8Q7gR72ftU3tJkCob0wh9itX4XEKgFGZBOsaGC6StPg39nAoY6tQPa1OutdfmdlRfVi8LcgLnRXCKEqsBxGZDe08EzatJ0Upnn63oiNy2EUU6KllOQGjmB+comHASiEmGaVxdDAOIl6N1zvWOxYbVegT+Oltgt7DjHggN/fxAVyZhpci2v+SuEsCaDDY35N5f4snS2GxVrhdTRxjMSLugeVGXSHlUOhQjCs4YO9nNkpGV9ANbOa6wyqwfTFKZubG+mKKMY=",
        "today": datetime.date.today().strftime("%Y%m%d"),
        "sortBy": "",
        "alertMsg": "",
        "ddlShareholdingDay": "%02d" % date.day,
        "ddlShareholdingMonth": "%02d" % date.month,
        "ddlShareholdingYear": "%04d" % date.year,
        "btnSearch.x": "29",
        "btnSearch.y": "12"
    }
    response = requests.post(
        "http://sc.hkexnews.hk/TuniS/www.hkexnews.hk/sdw/search/mutualmarket_c.aspx?t=sh",
        data=payload)

    return response.text


def parse_html(html_str):
    class my_parser(HTMLParser):

        def __init__(self):
            HTMLParser.__init__(self)
            self.shareholding_date = False
            self.get_date = False
            self.date = ""
            self.stock_stats = []
            self.in_tr = False
            self.in_td = False
            self.td_index = 0
            self.temp_stock_stats = []

        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)

            if tag == "div" and "id" in attrs and attrs["id"] == "pnlResult":
                # get Shareholding Date
                self.shareholding_date = True
            elif self.shareholding_date:
                self.get_date = True
            elif tag == "tr" and "class" in attrs and attrs["class"][0:3] == "row":
                # emter a valid <tr>
                self.in_tr = True
                self.td_index = 0
                self.temp_stock_stats = []
            elif tag == "td" and self.in_tr:
                # enter a valid <td>
                self.in_td = True

        def handle_endtag(self, tag):
            if tag == "tr" and self.in_tr:
                # leave <tr>, reset state
                self.in_tr = False
            elif tag == "td" and self.in_td:
                # leave <td>, reset state
                self.in_td = False

        def handle_data(self, data):
            if self.in_td:
                data = data.strip()
                if self.td_index == 2:
                    # turn '123,456,789' to '123456789'
                    data = data.replace(",", "")
                self.temp_stock_stats.append(data.strip())
                self.td_index += 1
                if self.td_index == 4:
                    # 4 <td>s in a <tr>
                    self.stock_stats.append(self.temp_stock_stats)
            elif self.get_date:
                self.date = data.strip()
                self.shareholding_date = False
                self.get_date = False

    hp = my_parser()
    hp.feed(html_str)
    hp.close()
    return hp.date, hp.stock_stats


def req(date):
    try:
        response_text = send_request(date)

        with open("%s-response.html" % (date), "w") as _:
            _.write(response_text)

        hdate, stats = parse_html(response_text)

        with open("%s-stats.txt" % (date), "w") as _:
            _.write("check: " + hdate + "\n")
            for s in stats:
                _.write("%-6s%10s%10s    %s\n" % (s[0], s[2], s[3], s[1]))

    except Exception:
        msg = "[%s] Error occured." % date
    else:
        m = re.match("(\d{1,2})/(\d{1,2})/(\d{4})", hdate[-10::])
        response_date = "%s-%s-%s" % (m.group(3),
                                      m.group(2).zfill(2), m.group(1).zfill(2))
        if response_date == str(date):
            msg = "[%s] Finished." % response_date
        else:
            msg = "[%s] Requested, but got [%s]" % (date, response_date)
    finally:
        with open("log.log", "a+") as _:
            print(msg)
            _.write(msg + "\n")


start_date = datetime.date(2017, 3, 17)
today_date = datetime.date.today()
current_date = start_date
while current_date < today_date:
    req(current_date)
    current_date += datetime.timedelta(days=1)
