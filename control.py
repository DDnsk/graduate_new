# coding=utf-8
__author__ = 'nsk'

from class_list import Article

def main(i):
    path = 'article_done/article_'+str(i)+'.html'
    tmp_case = Article(open(path))
    tmp_case.para_clean()
    tmp_case.preprocess_delete_empty_para()
    tmp_case.preprocess_seperate_sentences()
    tmp_case.preprocess_sentence2words()

    # tmp_case.display_test()
    # tmp_case.display_tables_figures()
    # tmp_case.display_references()
    # # tmp_case.display_keywords()
    # tmp_case.display_seperated_words()
    # for item in tmp_case.sentence_formalized_list:
    #     print 'the h2 index is %d' % item.h2_index
    #     print item.original_form
    # tmp_case.display_references()

    tmp_case.display_para_obj()


def statistic():
    count_down = 0
    for i in range(0, 100):
        path = 'article_done/article_'+str(i)+'.html'
        # print path
        try:
            tmp_case = Article(open(path))
            tmp_case.display_title()
            # tmp_case.display_test()
        except:
            print '%d is down' % i
            count_down += 1

    print 'there are 100 articles in total, %d is unable to process' % count_down

if __name__ == '__main__':
    main(0)
    # statistic()

