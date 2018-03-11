#!/usr/bin/env python3.6
import io
import sys
import shutil
import grequests


list_pictures_url = []

MAX_PARALLEL_CONNECTIONS = 50
OUTPUT_HTML = "output.html"
AGENT_WIN_OS = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) '\
               'Gecko/20100101 Firefox/52.0'
HEADER = {'User-Agent': AGENT_WIN_OS}
EXAMPLE_URL = 'https://raw.githubusercontent.com/bryangruneberg/' \
              'gsm-assessment-data/master/kafka.csv'

# pylint: disable=missing-docstring,unused-argument


def harvest_urls(response, **kwargs):
    cvs_text = response.text
    line = cvs_text.split()

    for pic_url in line[1:len(line)]:
        split_pic_url = pic_url.split(',')
        if len(split_pic_url) == 7:
            list_pictures_url.append(split_pic_url[6])


def save_file(filename_save_name, data):
    with open(filename_save_name, 'wb') as out_file:
        shutil.copyfileobj(data, out_file)
    del data


def download_pictures(response, **kwargs):
    name = str(response.request.url).split("=")[1]
    if response.status_code == 200:
        save_file(name + ".png", response.raw)
    else:
        print("Could not save: ", name, ".png"
              " - error code:", response.status_code,
              " http url: ", response.request.url)


def create_list_of_names(list_urls):
    for url in list_urls:
        if '=' in url:
            yield url.split("=")[1]


def create_html(list_of_pic_urls):

    picture_extension = ".png"

    table = []
    for picture_name in create_list_of_names(list_of_pic_urls):
        table.append("<td><img src='" + picture_name +
                     picture_extension + "\'></td>")

    max_elements = len(table)

    html = "<table>\n"
    for i in range(0, max_elements, 4):
        html = html + "<tr>\n"
        for j in range(0, min(4, max_elements-i)):
            html = html + table[i+j] + "\n"

        html = html + "</tr>\n"

    html = html + "</table>\n"
    html_byte = io.BytesIO(bytes(html, 'utf-8'))
    save_file(OUTPUT_HTML, html_byte)
    print("File", OUTPUT_HTML, "saved !!")


def exception_handler(request, exception):
    print('Exception on: ' + str(exception) + " for url: " + request.url)
    sys.exit(-1)


def get_url(url_list, function_ops):
    request_links = []
    for url_from_list in url_list:
        request_links.append(grequests.get(url_from_list,
                                           proxies=None,
                                           headers=HEADER,
                                           allow_redirects=False,
                                           hooks={'response': function_ops}))

    grequests.map(request_links,
                  exception_handler=exception_handler,
                  size=MAX_PARALLEL_CONNECTIONS,
                  gtimeout=5, stream=False)


if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("Usage: python ", sys.argv[0], " http[s]://URL_WITH_CSV")
        print("Example:\n"
              "       python", sys.argv[0], EXAMPLE_URL)
        sys.exit(0)

    URL_FROM_ARGUMENT = sys.argv[1]

    if URL_FROM_ARGUMENT.find("http") != -1:
        get_url([URL_FROM_ARGUMENT], harvest_urls)
        get_url(list_pictures_url, download_pictures)
        create_html(list_pictures_url)
    else:
        print("Url does not contain http|https: " + URL_FROM_ARGUMENT)
