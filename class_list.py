# coding=utf-8
__author__ = 'nsk'
import re
from bs4 import BeautifulSoup, element
import nltk
# import gensim

def para2sentence(para):
    """
    :param para: paragraph as input
    :return: a list, containing sentences as their original form
    """
    # split sentences using tools from nltk
    sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    sents = sent_tokenizer.tokenize(para)

    # fix some unexpected sentence-splitting problems
    sents_new = check_split_validity(sents)

    # clean the empty elements in the list
    sents_new_final = []
    for sentence in sents_new:
        if len(sentence) < 3:
            continue
        sents_new_final.append(sentence)

    return sents_new_final

def check_split_validity(list_input):
    """
    Since sentence splitting results could be imperfect, this function help with fix some of the splitting problems.
    (the appearance of 'i.e.' or 'Fig.' could result in unexpected splitting.)

    :param list_input: Sentence splitting results as list, with the help of
    nltk.data.load('tokenizers/punkt/english.pickle').
    :return:list_output: A new sentence list, merging sentences that are split unexpectedly.
    """
    ept_list = ['fig.', 'eqs.', 'i.e.', 'eq.', 'e.g.', 'e.g']  # to store the unexpected cases
    list_output = []
    flg = 0
    for sentence in list_input:
        if flg == 1:
            sentence = tmp_s + sentence
            flg = 0
        for ept in ept_list:
            if ept in sentence[-5:].lower():
                tmp_s = sentence
                flg = 1
                break
        if flg == 0:
            list_output.append(sentence)

    return list_output

class Article:
    def __init__(self, article_html):
        soup = BeautifulSoup(article_html, 'html5lib')
        self.para_list = []
        self.sentence_formalized_list = []
        self.title = soup.h1.string
        self.sub = []
        self.tables = {}
        self.figures = {}
        self.references = {}
        self.keywords = []
        flag = [0, 0, 0]  # [1, 1, 1] means that h2,h3,h4 all appear before respectly
        frag_sentence = ''

        for fragment in soup.find_all('div', id=re.compile('frag_(\d)+')):
            # Select all the fragments labeled with id numbers

            # print fragment['id']

            if fragment['id'] == 'frag_1':
                h1_tag = fragment.h1
                title_frag = ''
                for child in h1_tag.contents:
                    if type(child) == element.NavigableString:
                        title_frag += child

                self.title = title_frag
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
                    # print element_tmp.attrs

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
                            # tmp_part_h2 = Part()
                            # last_part = tmp_part_h2
                            # tmp_part_h2.title = element_tmp.string
                            # tmp_part_h2.isNormal = 0
                            # self.sub.append(tmp_part_h2)
                            continue

                    if element_tmp.name == 'ul':
                        for li in element_tmp.contents:
                            self.keywords.append(li.span.string)

                    if element_tmp.name == 'h2':
                        flag = [1, 0, 0]
                        if frag_sentence != '':
                            last_part.p.append(frag_sentence)
                            frag_sentence = ''
                        if 'reference' not in element_tmp.string.lower():
                            tmp_part_h2 = Part()
                            last_part = tmp_part_h2
                            tmp_part_h2.title = element_tmp.string
                            self.sub.append(tmp_part_h2)
                        if 'reference' in element_tmp.string.lower():
                            continue
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

                    if element_tmp.name == 'dl' and 'class' in element_tmp.attrs:
                        if element_tmp['class'] == ['listitem']:
                            sentences_set = ''
                            for dd in element_tmp.find_all('dd'):
                                for child in dd.contents:
                                    if child.name == 'p':
                                        for child_p in child.contents:
                                            if type(child_p) ==  element.NavigableString:
                                                sentences_set += child_p
                                            if type(child_p) == element.Tag:
                                                if child_p.name == 'span':
                                                    sentences_set += ' &&sy&& '
                                    if child.name == 'div'and 'class' in child.attrs:
                                        if child['class'] == ["formula"]:
                                            sentences_set += ' &&eq&& '

                                    if type(child) == element.NavigableString:
                                        sentences_set += child

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

                        sentences_set = ''
                        for sub_element in element_tmp.contents:
                            if type(sub_element) == element.NavigableString:
                                sentences_set += sub_element.replace(u'\xa0', ' ')
                            if type(sub_element) == element.Tag:
                                # print sub_element.attrs
                                if sub_element.name == 'span' and 'class' in sub_element.attrs:
                                    if sub_element['class'] == [u'mathmlsrc']:
                                        sentences_set += ' &&sy&& '  # symbol
                                        continue
                                if sub_element.name == 'span' and 'id' in sub_element.attrs:

                                    sentences_set += ' &&' + sub_element['id'] + '&& '
                                if sub_element.name == 'a' and 'id' in sub_element.attrs:

                                    sentences_set += ' &&' + sub_element['id'] + '&& '
                        if sentences_set == '':
                            continue

                        if flag == [1, 1, 1]:
                            tmp_part_h4.p.append(sentences_set)
                        if flag == [1, 1, 0]:
                            tmp_part_h3.p.append(sentences_set)
                        if flag == [1, 0, 0]:
                            tmp_part_h2.p.append(sentences_set)

                    if element_tmp.name == 'div' and 'class' in element_tmp.attrs:
                        if element_tmp['class'] == ["formula"]:
                            if last_part.p[-1].strip()[-1] != '.':
                                last_part.p[-1] += ' &&eq&& '
                            else:
                                frag_sentence += ' &&eq&& '  # equation

                        if element_tmp['class'] == [u'refText', u'svRefs']:
                            for li in element_tmp.ol.contents:
                                for reference_content in li.ul.contents:
                                    if reference_content['class'] == ['author']:
                                        reference_author = reference_content.string
                                    if reference_content['class'] == ['title']:
                                        reference_title = reference_content.string
                                    if reference_content['class'] == ['source']:
                                        reference_source = reference_content.string
                                self.references[li['id']] = [reference_author, reference_title, reference_source]

                    if element_tmp.name == 'span' and 'class' in element_tmp.attrs:
                        if element_tmp['class'] == ["mathmlsrc"]:
                            frag_sentence += ' &&sy&& '  # symbol

                    if element_tmp.name == 'div' and 'class' in element_tmp.attrs:
                        if element_tmp['class'] == ['figTblUpiOuter', 'svArticle']:
                            target = element_tmp.div.dl
                            object_description = ''
                            if 'id' in target.attrs:
                                object_id = target['id']
                                if object_id[0] == 'f':
                                    for description_frag in target.strings:
                                        object_description += description_frag
                                    self.figures[object_id] = object_description
                                if object_id[0] == 't':
                                    for description_frag in target.dd.strings:
                                        object_description += description_frag
                                    self.tables[object_id] = object_description

                if type(element_tmp) == element.NavigableString:
                    frag_sentence += element_tmp
                if element_tmp.name == 'em':
                    if element_tmp.string is None:
                        continue
                    frag_sentence += element_tmp.string.replace(u'\xa0', ' ')

        # print '*************************'

    def preprocess_delete_empty_para(self):
        for h2 in self.sub:
            del_list = []
            for paragraph in h2.p:
                if paragraph == '':
                    del_list.append(paragraph)
            for paragraph in del_list:
                h2.p.remove(paragraph)
            for h3 in h2.sub:
                del_list = []
                for paragraph in h3.p:
                    if paragraph == '':
                        del_list.append(paragraph)
                for paragraph in del_list:
                    h3.p.remove(paragraph)
                for h4 in h3.sub:
                    del_list = []
                    for paragraph in h4.p:
                        if paragraph == '':
                            del_list.append(paragraph)
                    for paragraph in del_list:
                        h4.p.remove(paragraph)

    def preprocess_seperate_sentences(self):
        for index_h2, h2 in enumerate(self.sub):
            if index_h2 == 0:
                continue
            for index_h2_para, h2_para in enumerate(h2.p):
                para_obj_tmp = Paragraph()
                para_obj_tmp.h2 = h2.title
                para_obj_tmp.h2_index = index_h2
                para_obj_tmp.para_index = index_h2_para
                self.para_list.append(para_obj_tmp)
                sents_new = para2sentence(h2_para)
                for index_in_para, sentence_new in enumerate(sents_new):
                    new_sentence_object = Sentence()
                    new_sentence_object.h2 = h2.title
                    para_obj_tmp.sentence_obj_list.append(new_sentence_object)
                    new_sentence_object.original_form = sentence_new
                    new_sentence_object.h2_index = index_h2
                    new_sentence_object.para_index = index_h2_para
                    new_sentence_object.in_para_index = index_in_para
                    self.sentence_formalized_list.append(new_sentence_object)
            for index_h3, h3 in enumerate(h2.sub):
                for index_h3_para, h3_para in enumerate(h3.p):
                    para_obj_tmp = Paragraph()
                    para_obj_tmp.h2 = h2.title
                    para_obj_tmp.h3 = h3.title
                    para_obj_tmp.h2_index = index_h2
                    para_obj_tmp.h3_index = index_h3
                    para_obj_tmp.para_index = index_h3_para
                    self.para_list.append(para_obj_tmp)
                    sents_new = para2sentence(h3_para)
                    for index_in_para, sentence_new in enumerate(sents_new):
                        new_sentence_object = Sentence()
                        new_sentence_object.h2 = h2.title
                        new_sentence_object.h3 = h3.title
                        para_obj_tmp.sentence_obj_list.append(new_sentence_object)
                        new_sentence_object.original_form = sentence_new
                        new_sentence_object.h2_index = index_h2
                        new_sentence_object.h3_index = index_h3
                        new_sentence_object.para_index = index_h3_para
                        new_sentence_object.in_para_index = index_in_para
                        self.sentence_formalized_list.append(new_sentence_object)
                for index_h4, h4 in enumerate(h3.sub):
                    for index_h4_para, h4_para in enumerate(h4.p):
                        para_obj_tmp = Paragraph()
                        para_obj_tmp.h2 = h2.title
                        para_obj_tmp.h3 = h3.title
                        para_obj_tmp.h4 = h4.title
                        para_obj_tmp.h2_index = index_h2
                        para_obj_tmp.h3_index = index_h3
                        para_obj_tmp.h4_index = index_h4
                        para_obj_tmp.para_index = index_h4_para
                        self.para_list.append(para_obj_tmp)
                        sents_new = para2sentence(h4_para)
                        for index_in_para, sentence_new in enumerate(sents_new):
                            new_sentence_object = Sentence()
                            new_sentence_object.h2 = h2.title
                            new_sentence_object.h3 = h3.title
                            new_sentence_object.h4 = h4.title
                            para_obj_tmp.sentence_obj_list.append(new_sentence_object)
                            new_sentence_object.original_form = sentence_new
                            new_sentence_object.h2_index = index_h2
                            new_sentence_object.h3_index = index_h3
                            new_sentence_object.h4_index = index_h4
                            new_sentence_object.para_index = index_h4_para
                            new_sentence_object.in_para_index = index_in_para
                            self.sentence_formalized_list.append(new_sentence_object)

    def display_title(self):
        print self.title

    def display_test(self):
        print self.title
        for item_h2 in self.sub:
            print item_h2.title
            for para_h2 in item_h2.p:
                print para_h2.encode('utf-8')
                print ''
            for item_h3 in item_h2.sub:
                print item_h3.title
                for para_h3 in item_h3.p:
                    print para_h3.encode('utf-8')
                    print ''
                for item_h4 in item_h3.sub:
                    print item_h4.title
                    for para_h4 in item_h4.p:
                        print para_h4.encode('utf-8')
                        print ''

    def display_targetted(self, h2, h3, h4):
        """
        in the process
        """
        if h4 == 0 and h3 == 0 and h2 != 0:
            for para in self.sub[h2].p:
                print para

    def para_clean(self):
        for h2 in self.sub:
            for para_h2 in h2.p:
                if para_h2 is None:
                    h2.p.remove(None)

    def display_title(self):
        print self.title

    def display_tables_figures(self):
        print 'Tables and Figures are as follows:'
        for k in self.tables:
            print k
            print self.tables[k]
        for k in self.figures:
            print k
            print self.figures[k]
        # print self.tables
        # print self.figures

    def display_references(self):
        print 'References are as follows:'
        for k in self.references:
            print k
            print self.references[k][1]

    def display_keywords(self):
        print 'Keywords are as follows:'
        for keyword in self.keywords:
            print keyword

    def display_seperated_words(self):
        for sentence_obj in self.sentence_formalized_list:
            print sentence_obj.seperated_words_list

    def preprocess_sentence2words(self):
        for sentence_obj in self.sentence_formalized_list:
            sentence_obj.seperated_words_list = re.split(r'\s+', sentence_obj.original_form)

    def display_para_obj(self):
        for para_obj in self.para_list:
            para_obj.display_content()

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

class Sentence:
    def __init__(self):
        self.h2 = ''
        self.h3 = ''
        self.h4 = ''
        self.h2_index = -1  # h2 index
        self.h3_index = -1  # h3 index
        self.h4_index = -1  # h4 index
        self.para_index = -1  # para index
        self.in_para_index = -1  # in-para index 在段落中第几句话

        self.original_form = ''
        self.seperated_words_list = []
        self.tfisf = {}
        self.special_unit = []  # to store something like ' &&br00005&& '

class Paragraph:
    def __init__(self):
        self.sentence_obj_list = []
        self.h2 = ''
        self.h3 = ''
        self.h4 = ''
        self.h2_index = -1  # h2 index
        self.h3_index = -1  # h3 index
        self.h4_index = -1  # h4 index
        self.para_index = -1  # para index

    def display_content(self):
        print '####This is %d h2' % self.h2_index
        print self.h2
        if self.h3_index != -1:
            print '###This is %d h3' % self.h3_index
            print self.h3
        if self.h4_index != -1:
            print '##This is %d h4' % self.h4_index
            print self.h4
        print '#This is %d paragraph' % self.para_index
        for sentence_obj in self.sentence_obj_list:
            print sentence_obj.original_form
