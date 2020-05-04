############################################ IMPORT STATEMENTS
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
import altair as alt 
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
import plotly.graph_objects as go
from datetime import datetime

############################################ TEXT FILES
files = ['j2015_1.txt', 'j2015_s.txt', 'j2015_2.txt', 'j2016_1.txt', 'j2016_s.txt', 'j2016_2.txt', 'j2017_1.txt', 'j2017_s.txt', 'j2017_2.txt', 'j2018_0.txt', 'j2019_1.txt', 'j2019_s.txt', 'j2019_2.txt']
path = "/Users/serena/Documents/the_journal_tracker_project/texts/"

######################################### MAIN FUNCTION
class CorpusWebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        query = parse.urlsplit(self.path).query
        query_dict = parse.parse_qs(query)
        print('QUERY DICT:', query_dict)
        if self.path == "/":
            self.send_header('Content-type','text/html; charset=utf-8')
            self.end_headers()
            f = open("jtp_front.html", encoding="utf-8")
            html = f.read()
            f.close()
            self.wfile.write(html.encode("utf-8"))
        elif "jtp_front.css" in self.path:
            self.send_header('Content-type','text/css; charset=utf-8')
            self.end_headers()
            f = open("jtp_front.css", encoding="utf-8")
            css = f.read()
            f.close()
            self.wfile.write(css.encode("utf-8"))
        elif "jtp_front.js" in self.path:
            self.send_header('Content-type','text/javascript; charset=utf-8')
            self.end_headers()
            f = open("jtp_front.js", encoding="utf-8")
            js = f.read()
            f.close()
            self.wfile.write(js.encode("utf-8"))
        elif 'search' in query_dict: 
            self.send_header('Content-type','text/html; charset=utf-8')
            self.end_headers()
            terms = query_dict['search'][0].split(", ")
            print("TERMS:", terms)
            sh = open("search_history.txt", "a")
            sh.write("DATE: " + str(datetime.now()))
            sh.write("\tSEARCH TERMS: " + str(terms) + "\n")
            sh.close()
            year = query_dict['years'][0]
            part = query_dict['parts'][0]
            filename = make_file(year, part)
            print("filenames:", filename)
            entries = preprocess_all(filename)
            fig, totals = search_test_full(entries, terms)
            fig.write_html("plotly.html", include_plotlyjs = 'cdn')
            chart = open('plotly.html').read()
            html2 = insert(totals, chart)
            f = open("debug.html", "w")
            f.write(html2)
            f.close()
            self.wfile.write(html2.encode("utf-8"))
            print('finished search')
        elif 'search' not in query_dict and 'parts' in query_dict: 
            self.send_header('Content-type','text/html; charset=utf-8')
            self.end_headers()
            year = query_dict['years'][0]
            part = query_dict['parts'][0]
            filename = make_file(year, part)
            print("filenames:", filename)
            entries = preprocess_all(filename)
            fig = count_all(entries)
            fig.write_html("plotly.html", include_plotlyjs = 'cdn')
            chart = open('plotly.html').read()
            html2 = insert2(chart, year, part)
            f = open("debug.html", "w")
            f.write(html2)
            f.close()
            self.wfile.write(html2.encode("utf-8"))
            print('finished count')
        if 'months' in query_dict: 
            self.send_header('Content-type','text/html; charset=utf-8')
            self.end_headers()
            year = query_dict['years'][0]
            month = query_dict['months'][0]
            day = query_dict['days'][0]
            files = make_file(year, '0')
            entries = preprocess_all(files)
            date, ent = find_entry(month, day, year, entries)
            text_shown = insert_text(date, ent)
            f = open("debug.html", "w")
            f.write(text_shown)
            f.close()
            self.wfile.write(text_shown.encode("utf-8"))
            print('finished text')

################################# MY FUNCTIONS

def find_entry(month, day, year, entries):
    """given a date (month has three letters) return the entry for that date"""
    mdict = {'Jan': 'January', 'Feb': 'February', 'Mar': 'March', 'Apr': 'April', 'May': 'May', 'Jun': 'June', 'Jul': 'July', 'Aug': 'August', 'Sep': 'September', 'Oct': 'October', 'Nov': 'November', 'Dec': 'December'}
    date = month + " " + day + " " + year
    if date in entries:
        return mdict[month] + " " + day + " " + year, entries[date].replace("\n", "<br>")
    return mdict[month] + " " + day + " " + year, "Sorry, this date is not currently available."

def count_all(entries): 
    """takes in a dict of entries and returns plotly plot of word counts"""
    dates, entryc = [], []
    for date, entry in entries.items():
        dates.append(" ".join([date.split(" ")[0][:3], date.split(" ")[1], date.split(" ")[2]]))
        entryc.append(len(entry.split(" ")))
    df = pd.DataFrame({'dates': dates, 'entries': entryc})
    fig = go.Figure()
    fig.add_trace(go.Scatter(x = df['dates'], y = df['entries'], mode = "none", hoveron = "fills+points",
                                fill = "tozeroy", fillcolor = '#8dd3c7',
                                hoverinfo = "y+x",
                                name = "",
                                opacity = 0.5))
    fig.update_layout(hovermode = 'x unified', plot_bgcolor = 'white')
    fig.update_xaxes(tickangle = 45, tickfont = dict(family = 'Arial', color = 'black', size = 12), nticks = 20, gridcolor = '#CDBEBC')
    fig.update_yaxes(gridcolor = '#CDBEBC')
    return fig

def insert(totals, graph):
    """insert results and graph"""
    f = open("jtp_front.html", encoding = "utf-8")
    html = f.read()
    f.close()
    all_totals = ""
    for item in totals:
        all_totals += "<br>" + "&emsp; " + item[0] + " &emsp; &emsp; &emsp; &emsp; " + str(item[1]) 
    html = html.replace('The results will appear here.', 'Here are the results and total number of occurrences: <b>' + all_totals + "</b>" + graph + "<br>")
    return html

def insert2(graph, year, part):
    """insert function for word count display"""
    f = open("jtp_front.html", encoding="utf-8")
    html = f.read()
    f.close()
    if year == "all":
        year = "January 2015 to December 2019"
        part = ""
    elif part == "0": 
        part = ""
    html = html.replace('The results will appear here.', 'Daily word count for <b>' + year + " " + part + ": </b><br>" + graph)
    return html

def insert_text(date, ent):
    """insert text"""
    f = open("jtp_front.html", encoding="utf-8")
    html = f.read()
    f.close()
    html = html.replace('The entry will appear here.', '<b style = "font-size: 28px; color: #443B57; letter-spacing: 5px;">' + date + '</b><br><br>' + ent)
    html = html.replace('<div id="Paris" class="w3-container city" style="display:none">', '<div id="Paris" class="w3-container city">')
    html = html.replace('<div id="Tokyo" class="w3-container city">', '<div id="Tokyo" class="w3-container city" style="display:none">')
    return html

def make_file(year, part):
    if year == "all":
        return files
    elif part == "0" and year != '2018':
        return ['j' + year + '_1.txt', 'j' + year + '_s.txt', 'j' + year + '_2.txt']
    else:
        return ['j' + year + "_" + part + '.txt']

def preprocess(text, year):
    """text is raw text, year is string"""
    reg = "((January|February|March|April|May|June|July|August|September|October|November|December) [0-9][0-9]?\n)"
    text2 = re.split(reg, text)
    entries = {}
    for i in range(len(text2)):
        if i == 1 or i % 3 == 1:
            entries[text2[i].split(" ")[0][:3] + " " + text2[i].split(" ")[1][:-1] + " " + year] = text2[i + 2]
    return entries

def preprocess_all(list_of_files):
    """opens and preprocesses all files, returns a dict of all files in order"""
    full_dict = None
    for i in range(len(list_of_files)):
        year = list_of_files[i][1:5]
        with open(path + list_of_files[i]) as f:
            f = f.read()
            entries = preprocess(f, year)
            if full_dict == None:
                full_dict = entries
            else:
                full_dict.update(entries)
    return full_dict

def search_text(entries, search):
    """searches journal text for string matches and returns a line chart showing frequency of those matches over time"""
    dates, results, term = [], [], []
    total = 0
    for entry in entries:
        result = [match.group() for match in re.finditer(search, entries[entry])]
        dates.append(entry)
        results.append(len(result))
        total += len(result)
        term.append(list(set(result)))
    return pd.DataFrame({'dates': dates, 'results': results, 'term': term}), total

def search_test_full(entries, list_of_terms):
    colors = ["#bebada", "#8dd3c7", "#fb8072", "#80b1d3", "#fdb462", "#b3de69", "#fccde5", "#d9d9d9", "#bc80bd", "#ccebc5"]
    count = 0
    fig = go.Figure()
    totals = []
    for term in list_of_terms:
        df, total = search_text(entries, term)
        totals.append((term, total))
        fig.add_trace(go.Scatter(x = df['dates'], y = df['results'], mode = "none", hoveron = "fills+points",
                                fill = "tozeroy", fillcolor = colors[count],
                                text = [", ".join(i) if len(i) > 0 else "" for i in df['term']],
                                hoverinfo = "text+y+x",
                                name = "",
                                opacity = 0.5))
        count += 1
    fig.update_layout(hovermode = 'x unified', plot_bgcolor = 'white')
    fig.update_xaxes(tickangle = 45, tickfont = dict(family = 'Arial', color = 'black', size = 12), nticks = 20, gridcolor = '#CDBEBC')
    fig.update_yaxes(gridcolor = '#CDBEBC')
    return fig, totals

########################################################

if __name__ == "__main__":
    http_port = 9990
    server = HTTPServer(('localhost', http_port),  CorpusWebServer)
    server.serve_forever()
