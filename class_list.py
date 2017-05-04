# coding=utf-8
__author__ = 'nsk'
import re
from bs4 import BeautifulSoup, element
import nltk

class Article:
    def __init__(self, article_html):
        soup = BeautifulSoup(article_html, 'html5lib')
        self.title = soup.h1.string
        self.sub = []
        flag = [0, 0, 0]  # [1, 1, 1] means that h2,h3,h4 all appear before respectly
        frag_sentence = ''

        for fragment in soup.find_all('div', id=re.compile('frag_(\d)+')):
            # Select all the fragments labeled with id numbers

            # print fragment['id']

            if fragment['id'] == 'frag_1':
                continue

            for element_tmp in fragment.contents:
                # Select all the tags and strings that are children of the id-fragments

                ####################################
                # code for test
                # if type(element_tmp) == element.Tag:
                #     print element_tmp.attrs
                # # print element_tmp
                # print type(element_tmp)
                # print '-----------------------'
                # print element_tmp.parent.id
                ####################################

                if type(element_tmp) == element.Tag:
                    if element_tmp.name == 'div' and 'class' in element_tmp.attrs:
                        if element_tmp['class'] == ['abstract', 'svAbstract', ''] or element_tmp['class'] == ['abstract', 'svAbstract']:
                            tmp_part_h2 = Part()
                            last_part = tmp_part_h2
                            tmp_part_h2.title = element_tmp.h2.string
                            if element_tmp.p.string is not None:
                                tmp_part_h2.p.append(element_tmp.p.string)
                            if element_tmp.p.string is None:
                                sentences_set = ''
                                for frag in element_tmp.p.contents:
                                    if type(frag) == element.NavigableString:
                                        sentences_set += frag
                                    if type(frag) == element.Tag:
                                        sentences_set += frag.string
                                tmp_part_h2.p.append(sentences_set)

                            tmp_part_h2.isNormal = 0
                            self.sub.append(tmp_part_h2)
                            continue

                    if element_tmp.name == 'h2' and 'class' in element_tmp.attrs:
                        if element_tmp['class'] == ['svKeywords']:
                            tmp_part_h2 = Part()
                            last_part = tmp_part_h2
                            tmp_part_h2.title = element_tmp.string
                            tmp_part_h2.isNormal = 0
                            self.sub.append(tmp_part_h2)
                            continue

                    if element_tmp.name == 'ul':
                        for li in element_tmp.contents:
                            tmp_part_h2.keyword.append(li.span.string)

                    if element_tmp.name == 'h2':
                        flag = [1, 0, 0]
                        if frag_sentence != '':
                            last_part.p.append(frag_sentence)
                            frag_sentence = ''

                        tmp_part_h2 = Part()
                        last_part = tmp_part_h2
                        tmp_part_h2.title = element_tmp.string

                        self.sub.append(tmp_part_h2)
                    if element_tmp.name == 'h3':
                        flag = [1, 1, 0]
                        if frag_sentence != '':
                            last_part.p.append(frag_sentence)
                            frag_sentence = ''

                        tmp_part_h3 = Part()
                        last_part = tmp_part_h3
                        tmp_part_h3.title = element_tmp.string
                        tmp_part_h2.sub.append(tmp_part_h3)

                    if element_tmp.name == 'h4':
                        flag = [1, 1, 1]
                        if frag_sentence != '':
                            last_part.p.append(frag_sentence)
                            frag_sentence = ''

                        tmp_part_h4 = Part()
                        last_part = tmp_part_h4
                        tmp_part_h4.title = element_tmp.string
                        tmp_part_h3.sub.append(tmp_part_h4)

                    # There are problems here, to be fixed
                    if element_tmp.name == 'dl' and 'class' in element_tmp.attrs:
                        if element_tmp['class'] == ['listitem']:
                            sentences_set = ''
                            for dd in element_tmp.find_all('dd'):
                                for string_single in dd.p.contents:
                                    if type(string_single) == element.NavigableString:
                                        sentences_set += string_single
                                    if type(string_single) == element.Tag:
                                        if string_single.name == 'span':
                                            sentences_set += '&&sy&&'
                                        if string_single.name == 'div':
                                            sentences_set += '&&eq&&'
                            if flag == [1, 1, 1]:
                                tmp_part_h4.p.append(sentences_set)
                            if flag == [1, 1, 0]:
                                tmp_part_h3.p.append(sentences_set)
                            if flag == [1, 0, 0]:
                                tmp_part_h2.p.append(sentences_set)

                    if element_tmp.name == 'p':
                        if frag_sentence != '':
                            last_part.p.append(frag_sentence)
                            frag_sentence = ''

                        if flag == [1, 1, 1]:
                            sentences_set = ''
                            for tmp_sentence in element_tmp.strings:
                                sentences_set += tmp_sentence.replace(u'\xa0', ' ')
                            if sentences_set == '':
                                continue
                            tmp_part_h4.p.append(sentences_set)
                        if flag == [1, 1, 0]:
                            sentences_set = ''
                            for tmp_sentence in element_tmp.strings:
                                sentences_set += tmp_sentence.replace(u'\xa0', ' ')
                            if sentences_set == '':
                                continue
                            tmp_part_h3.p.append(sentences_set)
                        if flag == [1, 0, 0]:
                            sentences_set = ''
                            for tmp_sentence in element_tmp.strings:
                                sentences_set += tmp_sentence.replace(u'\xa0', ' ')
                            if sentences_set == '':
                                continue
                            tmp_part_h2.p.append(sentences_set)

                    if element_tmp.name == 'div' and 'class' in element_tmp.attrs:
                        if element_tmp['class'] == ["formula"]:
                            if last_part.p[-1].strip()[-1] != '.':
                                last_part.p[-1] += ' &&eq&& '
                            else:
                                frag_sentence += ' &&eq&& '  # equation

                    if element_tmp.name == 'span' and 'class' in element_tmp.attrs:
                        if element_tmp['class'] == ["mathmlsrc"]:
                            frag_sentence += ' &&sy&& '  # symbol

                if type(element_tmp) == element.NavigableString:
                    frag_sentence += element_tmp
                if element_tmp.name == 'em':
                    if element_tmp.string == None:
                        continue
                    frag_sentence += element_tmp.string.replace(u'\xa0', ' ')

        # print '*************************'

    def display_title(self):
        print self.title

    def display_test(self):
        print self.title
        for item_h2 in self.sub:
            print item_h2.title
            for para_h2 in item_h2.p:
                print para_h2.encode('utf-8')
                print '*****'
            for item_h3 in item_h2.sub:
                print item_h3.title
                for para_h3 in item_h3.p:
                    print para_h3.encode('utf-8')
                    print '*****'
                for item_h4 in item_h3.sub:
                    print item_h4.title
                    for para_h4 in item_h4.p:
                        print para_h4.encode('utf-8')
                        print '*****'

    def display_targetted(self, h2, h3, h4):
        """
        in the process
        """
        if h4 == 0 and h3 == 0 and h2 != 0:
            for para in self.sub[h2].p:
                print para

    def clean(self):
        for h2 in self.sub:
            for para_h2 in h2.p:
                if para_h2 is None:
                    h2.p.remove(None)

class Part:
    def __init__(self):
        self.level = 0
        self.title = ''
        self.index = 0  # generated after the tree is built
        self.p = []
        self.sentence = []  # generated after the tree is built
        self.sub = []
        self.isNormal = 1
        self.keyword = []
