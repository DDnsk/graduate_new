# coding=utf-8
__author__ = 'nsk'

from class_list import Article

def main(i):
    path = 'article_done/article_'+str(i)+'.html'
    tmp_case = Article(open(path))
    tmp_case.clean()
    tmp_case.display_test()

def statistic():
    count_down = 0
    for i in range(0, 100):
        path = 'article_done/article_'+str(i)+'.html'
        # print path

        try:
            tmp_case = Article(open(path))
            # tmp_case.display_test()
        except:
            print '%d is down' % i
            count_down += 1

    print 'there are 100 articles in total, %d is unable to process' %count_down


if __name__ == '__main__':
    # main(1)
    statistic()

