#!/usr/bin/env python3.6
import sys
import shutil
import grequests

list_pictures_url = []

MAX_PARALLEL_CONNECTIONS = 50
AGENT_WIN_OS = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) '\
               'Gecko/20100101 Firefox/52.0'
HEADER = {'User-Agent': AGENT_WIN_OS}
EXAMPLE_URL = 'https://raw.githubusercontent.com/bryangruneberg/' \
              'gsm-assessment-data/master/kafka.csv'

# pylint: disable=missing-docstring,unused-argument



def harvest_urls(response, **kwargs):
    cvs_text = response.text
    line = cvs_text.split()

    for pic_url in line:
        if'http' in pic_url:
            split_pic_url = pic_url.split(',')
            if len(split_pic_url) == 7:
                if split_pic_url[6] not in list_pictures_url:
                    list_pictures_url.append(split_pic_url[6])


def save_pictures(name, response, url):
    filename_save_name = name + ".png"
    with open(filename_save_name, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response


def download_pictures(response, **kwargs):
    name = str(response.request.url).split("=")[1]
    if response.status_code == 200:
        save_pictures(name, response, response.request.url)
    else:
        print("Could not save: ", name, ".png"
              " - error with url: ", response.status_code)


def create_list_of_names(list_urls, extension):
    for url in list_urls:
        if '=' in url:
            yield url.split("=")[1] + extension


def save_html(html_output):
    html_filename_save_name = "output.html"
    with open(html_filename_save_name, 'w') as out_file:
        out_file.write(html_output)
    print("File " + html_filename_save_name + " saved !!")
    del html_output


def infinite_looper(objects):
    count = 0
    while True:
        if count >= len(objects):
            count = 0
        message = yield objects[count]
        if message is not None:
            count = 0 if message < 0 else message
        else:
            count += 1


def create_html(list_of_pic_urls):
    list_of_names = create_list_of_names(list_of_pic_urls, ".png")

    table_data = "\n".join('<td><img src=\'' + pic +
                           '\'></td>' for pic in list_of_names)
    table = table_data.split('\n')

    max_elements = len(table)
    table_generator = infinite_looper(table)
    html = "<table>\n"
    for i in range(0, max_elements, 4):
        html = html + "<tr>\n"
        for _ in range(0, min(4, max_elements-i)):
            html = html + table_generator.__next__() + "\n"

        html = html + "</tr>\n"

    html = html + "</table>\n"
    save_html(html)


def exception_handler(request, exception):
    print('Exception on: ' + str(exception) + " for url: " + request.url)
    sys.exit(-1)


def get_url(url_list, function):
    request_links = []
    for url_from_list in url_list:
        request_links.append(grequests.get(url_from_list,
                                           proxies=None,
                                           headers=HEADER,
                                           allow_redirects=False,
                                           hooks={'response': function}))

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
