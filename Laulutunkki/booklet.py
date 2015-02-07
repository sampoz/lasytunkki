#coding: utf-8
from Laulutunkki.models import *
from subprocess import call
from itertools import combinations
from django.core.files import File
import urllib
import os
import datetime


'''
one half page contain some what 70 lines to use
'''


#Creates booklet from given song objects with title and sorted to given order
def create_booklet(pages, author, booklet_title, front_page_text="", image_url=""):
    booklet = Booklet(title=booklet_title, author=author, pdf_file=None, front_page_text=front_page_text, front_page_image=image_url)
    booklet.save()
    create_booklet_pages(booklet, pages)
    return booklet


#Check if existing booklet is given, author is same and its resently created in
#order to update booklet otherwise create new booklet related to given existing
def update_or_create_booklet(songs, author, booklet_title, song_order, front_page_text="", image_url="", existing_booklet=None):
    booklet = None
    if existing_booklet is not None and \
       existing_booklet.author == author and \
       existing_booklet.created.replace(tzinfo=None) > datetime.datetime.now() - datetime.timedelta(days=7):
        update_booklet(existing_booklet, songs, booklet_title, song_order, front_page_text, image_url)
        booklet = existing_booklet
    else:
        pages = create_pages_song_lists(songs, song_order)
        booklet = create_booklet(pages, author, booklet_title, front_page_text, image_url)
        if existing_booklet is not None:
            booklet.previous_version = existing_booklet
            booklet.save()
    convert_booklet_to_pdf(booklet)
    return booklet


#Create songs object lists representing pages
def create_pages_song_lists(songs, song_order):
    max_lines = 70
    optimization_result = sort_songs_for_pages(songs, max_lines, song_order)
    return optimization_result_to_song_object_lists(songs, optimization_result)


def create_booklet_pages(booklet, pages):
    for i, page in enumerate(pages):
        booklet_page = BookletPage(booklet=booklet, page_number=i)
        booklet_page.save()
        for i, song in enumerate(page):
            booklet_song = BookletSong(booklet_page=booklet_page, song=song, order_no=i)
            booklet_song.save()


def update_booklet(booklet, songs, booklet_title, song_order, front_page_text="", image_url=""):
    if booklet is None or len(songs) == 0 or booklet_title is "" or len(song_order) == 0:
        raise Exception("All required fields to update booklet was not given")
    #Update title and front page text
    booklet.title = booklet_title
    booklet.front_page_text = front_page_text
    booklet.front_page_image = image_url
    booklet.pdf_file.delete()
    booklet.save()
    #Update pages
    #delete old pages
    for old_page in booklet.pages.all():
        old_page.songs.all().delete()
    booklet.pages.all().delete()
    #Create new pages
    pages = create_pages_song_lists(songs, song_order)
    create_booklet_pages(booklet, pages)


#####################################
##### Booklet page optimization #####
#####################################


#find fitting song order
def sort_songs_for_pages(song_objects, lines_in_page, song_order=[]):
    for song_id in song_order:
        if not song_objects.filter(id=song_id).exists():
            raise ValueError("Given song list and song order didn't match")
    songs_len = count_rows_for_songs(song_objects)
    return pages_optimization_simple(songs_len, lines_in_page, song_order)


#Count needed row count for songs
def count_rows_for_songs(songs):
    rows = {}
    if songs is not None:
        for song in songs:
            lines = count_rows_for_song(song)
            rows[song.id] = lines
    return rows


#Count needed row count for song
def count_rows_for_song(song):
    if song is not None:
        rows = song.lyrics.count('\r\n') + 1
        #Add header rows
        rows += 3
        return rows
    else:
        return 0


#Songs into pages so they won't go over
def pages_optimization_simple(songs_len, lines_in_page, song_order):
    pages = []
    comb = []
    left = lines_in_page
    #Add next song into empty or not full page until its full or no songs left
    #use full list (songs_len) if sub list is not defined as iterator
    for song in song_order:
        if songs_len[int(song)] < left or len(comb) is 0:
            comb.append(int(song))
            left -= songs_len[int(song)]
        else:
            break
    pages.append(comb)
    #If there is songs left iterate again
    if len(song_order[len(comb):]) > 0:
        page = pages_optimization_simple(songs_len, lines_in_page, song_order[len(comb):])
        pages += page
    return pages


#Takes optimization list and convert it to lists of song objects
def optimization_result_to_song_object_lists(songs, optimization_result):
    pages = []
    #convert tuple lists into list of song objects
    for opt_page in optimization_result:
        next_page = convert_song_ids_to_song_object_list(songs, opt_page)
        pages.append(next_page)
    return pages


#Convert given song id list to corresponding song object list
def convert_song_ids_to_song_object_list(songs, song_id_list):
    song_list = []
    for song_id in song_id_list:
        song = songs.get(id=song_id)
        song_list.append(song)
    return song_list


###############################################
##### Booklet conversion to latex and pdf #####
###############################################

#Create pdf file from given tex booklet
#Adds front page if exists in booklet
def convert_booklet_to_pdf(booklet):
    image_file = None
    #Try download booklet image if given
    if booklet.front_page_image:
        try:
            name = booklet.title[:10] + datetime.datetime.now().strftime('%Y%m%d%H%M%S')+".jpg"
            image_file, header = urllib.urlretrieve(booklet.front_page_image, 
                os.path.join("./media/booklet_images", name), reporthook)
        except Exception, e:
            remove_file_if_exists(name, "./media/booklet_images/")
            image_file = None
            raise Exception("Given image could not be loaded")
    
    #Create Tex code
    booklet_latex = booklet_to_tex_code(booklet, image_file)

    #Try create pdf file
    file_name = str(datetime.datetime.now().microsecond)
    with open(file_name + '.tex', 'wb') as f:
        f.write(booklet_latex)
    call(['pdflatex', file_name + '.tex'])
    if os.path.isfile(file_name + ".pdf"):
        with open(file_name + ".pdf") as f:
            name = booklet.title[:10] + datetime.datetime.now().strftime('%Y%m%d%H%M') + ".pdf"
            booklet.pdf_file.save(name, File(f))
    else:
        clean_up_pdf_creation_files(file_name, image_file)
        raise Exception("Error occured while creating pdf file form tex code.")

    #clean temporary files
    clean_up_pdf_creation_files(file_name, image_file)
    #return booklet.pdf_file


#Creates one half of page with given songs
def create_half_page(booklet_songs, song_number=1, page_number=" "):
    return r"""
      \fbox{
        \parbox[t][0.90\paperheight]{0.75\columnwidth}{
          """ + format_songs_for_page(booklet_songs, song_number) + r"""
          \vfill
          \hfill \tiny """+r"".join(str(page_number))+r"""
          \hfill \hfill
        }
      }
    """


#Handels song forming. Adds styling and song number and headers
def format_songs_for_page(booklet_songs, song_number=1):
    formated = r""
    number = song_number
    for booklet_song in booklet_songs:
        lyrics = booklet_song.song.lyrics.replace('\r\n', '\\\\')
        formated += r"""
          \normalsize
          \textbf{""" + r" ".join([str(number) + ".",  booklet_song.song.title]) + r"""}
          \medskip \\
          \small
          \hfill\parbox{0.73\columnwidth} {
              """ + r"".join(lyrics) + r"""
          \bigskip
          \smallskip
          }
        """
        number += 1
    return formated


#Creates LaTeX formated booklet with given pages
#pages is list of pages
def create_booklet_from_pages(pages):
    return r"""
      \documentclass[10pt, twocolumn, a4paper]{article}
      \usepackage[utf8]{inputenc}
      \usepackage{graphicx}
      \graphicspath{ {./media/booklet_images/} }
      \pagestyle{empty}
      \setlength\parindent{0pt}
      \batchmode

      \setlength{\textheight}{0.975\paperheight}
      \setlength{\textwidth}{0.975\paperwidth}
      \setlength\columnsep{5pt}
      \voffset=-1in
      \hoffset=-1in
      \topmargin = -20pt
      \oddsidemargin = 20pt
      \footskip = 0pt

      \begin{document}
      \setlength{\fboxsep}{20pt}
      """ + r" \newpage ".join(pages) + r"""
      \end{document}"""


#Create latex formated front page using booklet front page image
def create_booklet_front_page(booklet, image_file):
    text = r"""\parbox{0.73\columnwidth} {
              """ + r"".join(booklet.front_page_text) + r"""} \\\\"""
    if image_file:
        text += r"\includegraphics[width=0.7\columnwidth]{"+r"".join(image_file)+r"}"  
    return r"""
        \fbox{
            \parbox[t][0.90\paperheight]{0.75\columnwidth}{
                \hfill\vfill
                """ + r"".join(text) + r"""
                \hfill\vfill
            }
            
        }"""

     
#Sort pages for priting
def to_printing_order(pages):
    result = []
    empties = 0 if len(pages)%4 is 0 else 4 - len(pages)%4
    for i, p in enumerate(pages):
        if len(result)%4 is 0:
            if empties > 0:
                result.append(create_half_page([]))
                empties -= 1
            else:
                result.append(pages[-1])
                del pages[-1]
            result.append(p)
        else:
            result.append(p)
            if empties > 0:
                result.append(create_half_page([]))
                empties -= 1
            else:
                result.append(pages[-1])
                del pages[-1]
    return result


#Hook for image download which deternate if file is lager than allowed
def reporthook(blocknum, blocksize, totalsize):
    if totalsize > 1024*1024*10: #10mb max size
        raise Exception("Too large file, totalsize {}, maximum allowed 10mb".format(totalsize))


#Remove given file if it exist in path
def remove_file_if_exists(file_name, path=""):
    if os.path.isfile(path+str(file_name)):
        os.remove(path+file_name)


#Return booklet pages where songs are sorted in
def get_sorted_booklet_pages(booklet):
    sorted_booklet_pages = []
    booklet_pages = list(booklet.pages.all())
    for booklet_page in booklet_pages:
        booklet_page = list(booklet_page.songs.all())
        #Sort by order number
        booklet_page = sorted(booklet_page, key=lambda BookletSong: BookletSong.order_no)
        sorted_booklet_pages.append(booklet_page)
    return sorted_booklet_pages


#Clean up temp file needed for pdf creation
def clean_up_pdf_creation_files(file_name, image_file):
    remove_file_if_exists(file_name + ".tex")
    remove_file_if_exists(file_name + ".aux")
    remove_file_if_exists(file_name + ".log")
    remove_file_if_exists(file_name + ".pdf")
    remove_file_if_exists(image_file)


#Create tex code for pdf creation including page information
def booklet_to_tex_code(booklet, image_file):
    pages = []
    pages.append(create_booklet_front_page(booklet, image_file))
    song_number = 1
    raw_pages = get_sorted_booklet_pages(booklet)
    for i, page in enumerate(raw_pages):
        pages.append(create_half_page(page, song_number, i+1))
        song_number += len(page)
    pages = to_printing_order(pages)
    return create_booklet_from_pages(pages).encode('utf-8')