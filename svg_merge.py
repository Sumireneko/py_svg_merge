# ---------------------------------------------------
# Simple svg data merge v0.2
# ---------------------------------------------------
# Copyright (C) 2024 L.Sumireneko.M
# This script is replace insersion for data merge

# cd /Users/user/Desktop/py_svg_merge
# Python3 ./svg_merge.py

from lxml import etree
from io import StringIO
import re,os,time,copy

svgNS = 'http://www.w3.org/2000/svg'
etree.register_namespace('svg', 'http://www.w3.org/2000/svg')
etree.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
etree.register_namespace('krita', 'http://krita.org/namespaces/svg/krita')
etree.register_namespace('sodipodi', 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd')

# -----------------
# Settings
# -----------------

dir = "~/desktop/py_svg_merge/"
svg_path = dir+"test.svg"
csv_path = dir+"test_many.csv"

#svg_path = dir+"hagaki.svg"
#csv_path = dir+"hagaki.csv"

# export
export_file = 'output'


# data format
sp = ','
br = '\n'

# Places per page, 0:Place ALL
max_place = 0

# Column per row 
maxcol = 10

# override mode : if this flag is True and an impositon size > a document size,the document size override by the imposition size
override = True

# A4 size(300dpi) x=2480 y=3508
docx = 240
docy = 358

# Recommend Padding (unit:px)
# 300dpi :  1mm = 11.8px , 5mm = 59px  , 10mm = 108px  , 15mm = 177px
# 600dpi :  1mm = 23.6px , 5mm = 108px , 10mm = 236px  , 15mm = 344px

padx = 10
pady = 10

# Distination pos (unit:px)
dx = 100
dy = 100

# -----------------
# Mode Setting
# -----------------
# template.svg  %%TITLE%% %%NAME%% %%CITY%% %%COLOR%%
# The words for replace in test.csv:
# TITLE,NAME,CITY,COLOR
# aaa,bbb,ccc,ddd
# Replace as %%TITLE%% to aaa,%%NAME%% to bbb ....

# tag
lt = '%%'
gt = '%%'


# Time
old_tim = 0

# -----------------
# Utilites
# -----------------
def time_calc(mes,st):
    global old_tim
    n = time.time()
    e = n - st
    e = round(e, 3)
    d = round( e - old_tim ,3)
    old_tim = e
    print(f' {mes} TIME: {e} (+ {d}) ')

# -----------------
# Sub Process
# -----------------

# Load text file 
def read_file(path):
    print(f"- Loading file: {path}")
    if not path:
        return
    full_path = os.path.expanduser(path)
    f = open(full_path, 'r', encoding='UTF-8')
    data = f.read()
    f.close()
    #print('File data:'+data)
    return str(data)


def read_svg(path):
    print(f"- Loading file: {path}")
    if not path:
        return
    full_path = os.path.expanduser(path)
    data = etree.parse(full_path)
    return data



def save_file(path,sdata):
    # mode w,x
    print(f"- Save file: {path}")
    try:
        with open(path, mode='w', encoding='UTF-8') as f:
            f.write(sdata)
    except FileExistsError:
        pass

def create_svg(w,h):
    # w = 800
    # h = 600
    root_xml = '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" >\n</svg>'
    new_root = etree.fromstring(root_xml)
    new_root.set('width',str(w))
    new_root.set('height',str(h))
    new_root.set('viewBox',f"0 0 {w} {h}")
    #print(etree.tostring(new_root))
    style = etree.Element("style", type="text/css")
    style.text = etree.CDATA("/** CSS **/")
    new_root.insert(0, style)
    
    return new_root



# -----------------
# Main
# -----------------
def getStrByPath(tree,xpath):
    return ''.join([str(s) for s in tree.xpath(xpath)[0]])


def getIntByPath(tree,xpath):
    a = ''.join([str(s) for s in tree.xpath(xpath)[0]])
    a = re.sub(r'(px|pt|mm)','',a)
    return int(float(a))



def main():
    global docx,docy,padx,pady,dx,dy,maxcol,max_place
    st = time.time()
    time_calc('Start ',st)

    # read csv file
    csvdata = read_file(csv_path)
    list = csvdata.split(br) # more split
    tags = list.pop(0).split(sp)
    
    page,pdx,idx = 0,0,0

    # read svg file
    svgtree = read_svg(svg_path)
    
    w = getIntByPath(svgtree,'//*[name()="svg"]/@width' )
    h = getIntByPath(svgtree,'//*[name()="svg"]/@height' )
    #print("debug:",type(w))


    #set document size

    max_width = dx*2+(maxcol*(w+padx))
    maxrow = (len(list)+maxcol) // maxcol
    max_height = dy*2+(maxrow*(h+pady))
    
    up_row = (max_place+maxcol) // maxcol
    up_height = dy*2+(up_row*(h+pady))
    
    if override == True:
        if docx < max_width: docx = max_width
        if docy < max_height:
            if max_place > 0:max_height = up_height
            docy = max_height

    new_svgtree = create_svg(max_width,max_height)
    up_max = max_place
    
    for li in list:
        p = li.split(sp)
        n = f'New{idx}'
        nid = etree.Element("g", id=n)
        tmpl = copy.deepcopy(etree.tostring(svgtree).decode('UTF-8'))

        if up_max > 0 and idx > 0 and idx % up_max == 0:
            # Save the document
            new_svgdata = etree.tostring(new_svgtree).decode('utf-8')
            save_file(f'./{export_file}{page}.svg', new_svgdata)
            
            # Add new document
            new_svgtree = create_svg(max_width,max_height)
            page += 1
            pdx,row,col = 0,0,0

        mat,rdx = 0,0
        for r in p:
            pat = f'{lt}{tags[rdx]}{gt}'
            #print("Reg:"+pat)
            if (re.search(pat,tmpl)):
                mat += 1
                tmpl = tmpl.replace(pat,r)
            rdx += 1
        
        ptmpl = etree.parse(StringIO(tmpl))
        for k in ptmpl.findall(".//{*}g"):
            kid = k.get('id')
            k.set('id',kid+"_"+str(idx))
            nid.append(k)
        #print("id:"+str(id))
        
        col = pdx % maxcol # 0123401234...
        row = 0 if pdx == 0 else pdx // maxcol
        tx,ty = dx+(col*(w+padx)), dy+(row*(h+pady))
        
        nid.set('transform', f'matrix(1 0 0 1 {tx} {ty})' )
        new_svgtree.append(nid)
        idx += 1
        pdx += 1


    
    new_svgdata = etree.tostring(new_svgtree).decode('utf-8')
    #print(new_svgdata)
    save_file(f'./{export_file}{page}.svg', new_svgdata)
    
    time_calc('Finish',st)


main()