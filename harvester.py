import grequests
import shutil
import sys

reqs = []
list_pictures_url = []

agent_win_os = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0'
header = {'User-Agent': agent_win_os}


def harvest_urls(response,**kwargs):
    status_code = response.status_code
    cvs_text = response.text
    line = cvs_text.split()

    for pic_url in line:
      if'http' in pic_url:
         split_pic_url =  pic_url.split(',')
         if len(split_pic_url) == 7:
            if split_pic_url[6] not in list_pictures_url:
               list_pictures_url.append(split_pic_url[6])

def save_pictures(name, response, url):
    filename_save_name = name + ".png"

    if response.status_code == 200:
        with open(filename_save_name, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response

def rip_name_from_url(url_pic):

    if url_pic.find("=") != -1:
        return url_pic.split("=")[1]
    else:
        print("Url: " + url_pic + " is not valid !!! ")
        exit(0)

def download_pictures(response, **kwargs):
    name = rip_name_from_url(response.request.url)
    save_pictures(name, response,response.request.url)

def create_list_of_names(list_urls,extenstion):
    list_names = []
    for url in list_urls:
        list_names.append(rip_name_from_url(url) + extenstion)
    return list_names

def create_table(list_of_pic):

    table = "\n".join('<td><img src=\''+pic+'\'></td>' for pic in list_of_pic)
    return table

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
        if message != None:
            count = 0 if message < 0 else message
        else:
            count += 1


def create_html(list_of_pic_urls):
    list_of_names = []
    list_of_names = create_list_of_names(list_of_pic_urls,".png")

    html = "<table>\n"

    table_data = create_table(list_of_names)
    table = table_data.split('\n')
    max_elements = len(table)
    table_generator = infinite_looper(table)
    for i in range(0,max_elements, 4):
       html += "<tr>\n"
       for j in range(0,4):
           if j+i < max_elements:
              html += table_generator.__next__() + "\n"

       if i < max_elements:
          html += "</tr>\n"

    html += "</table>\n"
    save_html(html)

def exception_handler(request, exception):
    print('Grequests Exception on: ' + str(exception))
    print('We are closing app!!')
    sys.exit(-1)

def get_url(url_list, function_operation):
  for url in url_list:
     reqs.append(grequests.get(url, proxies=None, headers=header,
                            allow_redirects=False, hooks={'response': function_operation}))

  grequests.map(reqs, exception_handler=exception_handler, size=50, gtimeout=5, stream=False)



if __name__ == '__main__':

  if len(sys.argv) < 2:
        print("Usage: python ", sys.argv[0], " http[s]://URL_WITH_CSV")
        print("Example:\n python " + sys.argv[0], "https://raw.githubusercontent.com/bryangruneberg/gsm-assessment-data/master/kafka.csv")
        sys.exit(0)
  
  url = sys.argv[1]
  if url.find("http") != -1:
     get_url([url],harvest_urls)
     get_url(list_pictures_url,download_pictures)
     create_html(list_pictures_url)
  else:
      print("Url does not contain http|https: " + url)
