## How to run
For running this app you need python3.5(minimum), pip and git
Clone app from git:
```
git clone https://github.com/vladimirc81/harvester.git
```
Move to dir with py app

```
cd harvester/
```
Install library need for running app:
```
pip install -r requirements.txt
```

Run app with:
```
pythone harvester.py  https://some/urls/txt.cvs
```

If everthing goes ok there would be bunch of png files with one output.html.
This simple version missing:
- output html file naming
- directory output
- verification if files are ok (png and html)
- more errors description if something goes wrong 
