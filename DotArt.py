import cv2
from optparse import OptionParser

COLOR = 255
EMPTY_SPACES = False

tb_threshold= 'threshold'
tb_scale = 'width'
tb_type = 'type'
title_window="OPTIONS"

def get_symbol(img, i, j):
    (h, w) = img.shape
    symbol = 0 
    if (i+3 < h and j+1 < w):
        symbol += 1 if img[i]  [j] ==COLOR else 0
        symbol += 2 if img[i+1][j] ==COLOR else 0
        symbol += 4 if img[i+2][j] ==COLOR else 0

        symbol += 8  if img[i]  [j+1]==COLOR else 0
        symbol += 16 if img[i+1][j+1]==COLOR else 0
        symbol += 32 if img[i+2][j+1]==COLOR else 0

        symbol += 64  if img[i+3][j]  ==COLOR else 0
        symbol += 128 if img[i+3][j+1]==COLOR else 0
    if (EMPTY_SPACES and symbol == 0) : symbol = 1
    return chr(10240 + symbol)

def translate_cv2(img):
    (h, w) = img.shape
    ASCII_art = ""
    for i in range(0, h, 4):
        for j in range(0, w, 2):
            ASCII_art += get_symbol(img, i,j)
        ASCII_art += '\n'
    return ASCII_art

def img_size(img, scale): 
    width = img.shape[1] * scale / 100
    height = img.shape[0] * scale / 100
    width -= width%4
    height -= height%2
    return (int(width), int(height)) 

def resize_img(img, scale):            
    sz = img_size(img, scale)
    resize = cv2.resize(img, sz, interpolation = cv2.INTER_AREA)
    return resize

def do_nothing(val):
    pass

def init_wnd():
    cv2.namedWindow(title_window)
    cv2.resizeWindow(title_window, 384, 90)
    cv2.createTrackbar(tb_threshold,  title_window, 0, 255, do_nothing)
    cv2.createTrackbar(tb_scale,  title_window, 100, 100, do_nothing)
    cv2.createTrackbar(tb_type,  title_window, 0, 1, do_nothing)

def cv_2_wnd_threshold(img):    
    init_wnd()
    info = cv2.resize(img, (384,120), interpolation = cv2.INTER_AREA)
    info[:] = 255
    result = img

    while (True):
        scale = cv2.getTrackbarPos(tb_scale,  title_window)
        if scale > 0: result = resize_img(img, scale)  

        val = cv2.getTrackbarPos(tb_threshold,  title_window)
        switch  = cv2.THRESH_BINARY if cv2.getTrackbarPos(tb_type,  title_window) > 0.5 else cv2.THRESH_BINARY_INV
        _, result = cv2.threshold(result, val, 255, switch)

        info = cv2.putText(info, f'{result.shape[0]}, {result.shape[1]}, {result.shape[0]*result.shape[1]/8}', (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, 0)
        cv2.imshow('IMAGE', result) 
        cv2.imshow(title_window, info) 
        info[:] = 255
        cv2.resizeWindow('IMAGE', result.shape[1], result.shape[0])
        k = cv2.waitKey(1) & 0xFF        
        if (k == 27):
            break;
        

    cv2.destroyAllWindows()
    return result

if __name__ == "__main__":
    usage = 'usage: %prog [options]'
    parser = OptionParser()
    parser.add_option("-i", "--image", dest="inputfile", 
                  help="input image", metavar="IMAGE")
    parser.add_option('-o', '--output', dest='outputfile',
                  help='output file')
    parser.add_option('-c', '--constraints', dest='constraints',
                  help='constraints on count of output symbols')
    parser.add_option('-e', '--emptyspaces', dest='emptyspaces',
                  help='remove empty spaces', action='store_true', default=False)
    (options, args) = parser.parse_args()


    inputfile =  options.inputfile if (options.inputfile) else None
    outputfile =  options.outputfile if (options.outputfile) else None
    constraints =  int(options.constraints) if (options.constraints) else 1500
    EMPTY_SPACES = options.emptyspaces

    #print(f'[-i = {inputfile}] [-o = {outputfile}] [-c = {constraints}] [-es = {EMPTY_SPACES}]\n')

    if (not inputfile is None):        
        img = cv2.imread(inputfile)    
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv_2_wnd_threshold(img)
        art = translate_cv2(img)
        if (len(art) < constraints):
            print(art)
        if (not outputfile is None):
            with open(outputfile, "w", encoding="UTF-8") as text_file:
                print(art, file=text_file)
    