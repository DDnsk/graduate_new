# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
__author__ = 'nsk'
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier

import logging
import heapq
from scipy.cluster.hierarchy import ward, dendrogram
import matplotlib.pyplot as plt
import matplotlib as mpl

from sklearn.manifold import MDS

from class_list import Article

def rank_sentences(sentence_list, top_n, w_position, w_isf, w_TFR):
    # print 'there are %d sentences for chosen' % sentence_list.__len__()
    score_list = []
    for sentence_obj in sentence_list:
        position_score = 0
        if sentence_obj.in_para_index != -1:
            position_score = 1/float(sentence_obj.in_para_index + 1)

        isf_score = 0
        for k in sentence_obj.isf:
            isf_score += sentence_obj.isf[k]

        table_fig_ref_score = len(sentence_obj.tables) + len(sentence_obj.figures) + len(sentence_obj.references)
        score_list.append(w_position*position_score + w_isf*isf_score - w_TFR*table_fig_ref_score)

    top_n_scores_list = heapq.nlargest(top_n, score_list)
    top_n_sentences_list = []
    for i, score in enumerate(score_list):
        if score in top_n_scores_list:
            top_n_sentences_list.append(sentence_list[i])
    return top_n_sentences_list

def sentences_merge(sentence_list):
    dict_merge_tf = {}
    dict_merge_isf = {}
    for sentence_obj in sentence_list:
        for k in sentence_obj.tf:
            if dict_merge_tf.has_key(k):
                dict_merge_tf[k] += sentence_obj.tf[k]
            else:
                dict_merge_tf[k] = sentence_obj.tf[k]
        for k in sentence_obj.isf:
            dict_merge_isf[k] = sentence_obj.isf[k]
    return dict_merge_isf

# To be continued
class featured_Article:
    def __init__(self):
        self.title = ''
        self.general_background_1_para_list = []
        self.specific_2_para_list = []
        self.general_method_3_para_list = []
        self.experiment_5_para_list = []
        self.method_specific_4_para_list = []
        self.experiment_specific_6_para_list = []
        self.fulltext_7_para_list = []
        self.conclusion_8_para_list = []
        self.structure_9_para_list = []
        self.vector = []

    # working
    def para2sentence(self):
        list_1 = []
        for para_obj in self.general_background_1_para_list:
            for sentence_obj in para_obj.sentence_obj_list:
                list_1.append(sentence_obj)
        chosen_1_sentences_list = rank_sentences(list_1, 2, 1, 1, 0.5)

        list_3 = []
        for para_obj in self.general_method_3_para_list:
            for sentence_obj in para_obj.sentence_obj_list:
                list_3.append(sentence_obj)
        chosen_3_sentences_list = rank_sentences(list_3, 2, 1, 0.5, 1)

        list_5 = []
        for para_obj in self.experiment_5_para_list:
            for sentence_obj in para_obj.sentence_obj_list:
                list_5.append(sentence_obj)
        chosen_5_sentences_list = rank_sentences(list_5, 2, 1, 1, 1)

        list_7 = []
        for para_obj in self.fulltext_7_para_list:
            for sentence_obj in para_obj.sentence_obj_list:
                list_7.append(sentence_obj)
        chosen_7_sentences_list = rank_sentences(list_7, 2, 1, 1, 1)

        self.vector.append(chosen_1_sentences_list)
        self.vector.append(chosen_3_sentences_list)
        self.vector.append(chosen_5_sentences_list)
        self.vector.append(chosen_7_sentences_list)

    def display(self):
        print '1'
        for paragraph in self.general_background_1_para_list:
            paragraph.display_content_slim()

# 一个维度多个句子组成列表的相似度计算
def sentence_list_similarity(sentence_list_1, sentence_list_2):

    # 如果句子列表为空则直接返回相似度0
    if len(sentence_list_2) == 0 or len(sentence_list_1) == 0:
        return 0
    # 先将句子列表合并，成为一个字典
    dict_1 = sentences_merge(sentence_list_1)
    dict_2 = sentences_merge(sentence_list_2)

    # 初始化
    similarity = 0

    for k in dict_1:
        if k in dict_2:
            similarity += dict_1[k]*dict_2[k]

    return similarity

# 两篇论文之间的相似度，由向量之间的相似度计算得到
def similarity_between_vectors(art_1, art_2):
    similarity_final = 0

    similariry_socre_background = sentence_list_similarity(art_1[0], art_2[0])

    similariry_socre_method = sentence_list_similarity(art_1[1], art_2[1])

    similariry_socre_experiment = sentence_list_similarity(art_1[2], art_2[2])

    similariry_socre_fulltext = sentence_list_similarity(art_1[3], art_2[3])

    similarity_final = similariry_socre_background + 0.5*similariry_socre_method + 0.5*similariry_socre_experiment + similariry_socre_fulltext
    # print '%f = %f + %f + %f + %f' % (similarity_final,similariry_socre_background,similariry_socre_method,similariry_socre_experiment,similariry_socre_fulltext)

    return similarity_final

# 计算两两论文间的相似度
def calculate_article_similarity(featured_article_list):
    gephi_edge_file = open('gephi_edge.csv', 'w')
    similarty_matrix = []
    for i, article_1 in enumerate(featured_article_list):
        line_i = []
        for j, article_2 in enumerate(featured_article_list):
            # print similarity_between_vectors(article_1.vector, article_2.vector)
            # 输出到矩阵里
            line_i.append(similarity_between_vectors(article_1.vector, article_2.vector))
            # 输出到两两gephi
            # if i != j:
            #     write_to_gephi_edge(i, j, similarity_between_vectors(article_1.vector, article_2.vector), gephi_edge_file)
        similarty_matrix.append(line_i)
    return similarty_matrix

def write_to_gephi_edge(i, j, edge_weight, gephi_edge_file):
    token = ';'
    line = str(i) + token + str(j) + token + str(edge_weight) + '\n'
    gephi_edge_file.write(line)

def write_to_gephi_nodes(feature_article_list):
    gephi_nodes_file = open('gephi_nodes.csv', 'w')
    token = ';'
    for i, article in enumerate(feature_article_list):
        line = str(i) + token + article.title + '\n'
        gephi_nodes_file.write(line)

def train_f():
    valid_list = get_valid_index_final()
    manually_annotated_article_list = [0, 1, 3, 4, 6, 7, 8, 9, 10, 11]

    file_annotation_answers = open('annotation_answers_2.csv', 'r')
    list_annotation_answers = []
    for line in file_annotation_answers.readlines():
        for answer in line.split(','):
            if answer != '' and answer != '\n':
                try:
                    list_annotation_answers.append(int(answer))
                except:
                    print answer
                    print type(answer)
    list_annotation_vector = []
    for i in manually_annotated_article_list:
        path = 'article_done/article_'+str(valid_list[i])+'.html'
        try:
            tmp_case = Article(open(path))
            tmp_case.para_clean()
            tmp_case.preprocess_delete_empty_para()
            tmp_case.preprocess_seperate_sentences()
            tmp_case.preprocess_extract_special_elements()
            tmp_case.preprocess_sentence2words()
            tmp_case.preprocess_tables_figures()  # clean unexpected tokens
            tmp_case.preprocess_tfisf()
            vector_list_tmp, feature_name_list = tmp_case.preprocess_para_extract_features()
            # print vector_list_tmp.__len__()
            for vector in vector_list_tmp:
                list_annotation_vector.append(vector)
        except:
            logging.exception("exception")

    # 决策树
    # clf = tree.DecisionTreeClassifier(max_features='log2')
    # clf = clf.fit(list_annotation_vector, list_annotation_answers)

    # 随机森林
    clf = RandomForestClassifier()
    clf = clf.fit(list_annotation_vector, list_annotation_answers)

    # print out the decision tree
    # tree.export_graphviz(clf, out_file='tree_without_cuting.dot', feature_names=feature_name_list)

    return clf  # return the well_trained decision tree

def predict_f(decision_tree):

    # remove the annoted articles
    valid_list = get_valid_index_final()
    manually_annotated_article_list = [0, 1, 3, 4, 6, 7, 8, 9, 10, 11]
    for index in manually_annotated_article_list:
        if index in valid_list:
            valid_list.remove(index)

    # for each article in testing set, extract its features,  predict its paragraphs' class, append them to
    # featured_Article class, for following processing
    featured_article_tmp_list = []
    for index in valid_list[0:101]:
        try:
            path = 'article_done/article_'+str(valid_list[index])+'.html'
            tmp_case = Article(open(path))
            tmp_case.para_clean()
            tmp_case.preprocess_delete_empty_para()
            tmp_case.preprocess_seperate_sentences()
            tmp_case.preprocess_extract_special_elements()

            tmp_case.fullfill_ref_tab_fig()  # 将文中的参考文献、图表全部以标题的形式纳入语句

            tmp_case.preprocess_sentence2words()
            tmp_case.preprocess_tables_figures()  # clean unexpected tokens
            tmp_case.preprocess_tfisf()
            vector_list_tmp, feature_name_list = tmp_case.preprocess_para_extract_features()
            paragraph_classification = decision_tree.predict(vector_list_tmp)
            # print paragraph_classification
            featured_article_tmp = featured_Article()
        except:
            continue

        for i, type in enumerate(paragraph_classification):
            if type == 1:
                featured_article_tmp.general_background_1_para_list.append(tmp_case.para_list[i])
            if type == 2:
                featured_article_tmp.specific_2_para_list.append(tmp_case.para_list[i])
            if type == 3:
                featured_article_tmp.general_method_3_para_list.append(tmp_case.para_list[i])
            if type == 4:
                featured_article_tmp.method_specific_4_para_list.append(tmp_case.para_list[i])
            if type == 5:
                featured_article_tmp.experiment_5_para_list.append(tmp_case.para_list[i])
            if type == 6:
                featured_article_tmp.experiment_specific_6_para_list.append(tmp_case.para_list[i])
            if type == 7:
                featured_article_tmp.fulltext_7_para_list.append(tmp_case.para_list[i])
            if type == 8:
                featured_article_tmp.conclusion_8_para_list.append(tmp_case.para_list[i])
            if type == 9:
                featured_article_tmp.structure_9_para_list.append(tmp_case.para_list[i])
        featured_article_tmp.title = tmp_case.title
        featured_article_tmp.para2sentence()
        # for item in featured_article_tmp.vector:
        #     if len(item) == 0:
        #         continue
        featured_article_tmp_list.append(featured_article_tmp)
    simi_matrix = calculate_article_similarity(featured_article_tmp_list)
    write_to_gephi_nodes(featured_article_tmp_list)
    return simi_matrix, featured_article_tmp_list

def main(end):
    valid_list = get_valid_index_final()
    for i in range(0, end):
        path = 'article_done/article_'+str(valid_list[i])+'.html'
        try:
            tmp_case = Article(open(path))
            tmp_case.para_clean()
            tmp_case.preprocess_delete_empty_para()
            tmp_case.preprocess_seperate_sentences()
            tmp_case.preprocess_extract_special_elements()
            tmp_case.preprocess_sentence2words()
            tmp_case.preprocess_tables_figures()  # clean unexpected tokens
            tmp_case.preprocess_tfisf()
            tmp_case.paragraph_obj2file(i)

            # display output
            # tmp_case.display_para_obj()
            # tmp_case.display_references()
            # tmp_case.display_tables_figures()
        except:
            logging.exception("exception")

def statistic(valid_index_list):
    count_down = 0
    article_obj_list = []
    for i in valid_index_list:
        path = 'article_done/article_'+str(i)+'.html'
        # print path
        try:
            tmp_case = Article(open(path))
            article_obj_list.append(tmp_case)
            # tmp_case.display_test()
        except:
            print '%d is down' % i
            count_down += 1
            continue

    print 'there are 100 articles in total, %d is unable to process' % count_down

def write_valid_html_file_index_list_to_file(valid_index_list):
    """
    :param valid_index_list: valid index of html file which is generated by function:get_valid_html_index_list()
    :return:No return here. The function will write the index of valid html file checked by Article class to file,
    each index in a line.
    """
    file_tmp = open('valid_html_file_index_list.txt', 'w')
    for i in valid_index_list:
        path = 'article_done/article_'+str(i)+'.html'
        try:
            tmp_case = Article(open(path))
            tmp_case.para_clean()
            tmp_case.preprocess_delete_empty_para()
            tmp_case.preprocess_seperate_sentences()
            tmp_case.preprocess_sentence2words()
            if tmp_case.title != '' and tmp_case.title != None and len(tmp_case.sentence_formalized_list) > 150:
                file_tmp.write(str(i)+'\n')
                print i
        except:
            continue

def get_valid_html_index_list():
    """
    :return: valid index of html file. The validity is checked by crawler.
    """
    file_tmp = open('1-1000.csv', 'r')
    valid_html_index_list = []
    for line in file_tmp.readlines():
        seperated_fields_tmp = line.split(',')
        index_now = int(seperated_fields_tmp[0])
        length_now = int(seperated_fields_tmp[-1].strip())
        timeout_or_not = seperated_fields_tmp[-2]
        if length_now > 100000 or timeout_or_not == 'finished':
            valid_html_index_list.append(index_now)
    return valid_html_index_list

def get_valid_index_final():
    """
    :return:list; get the final valid index from file generated by write_valid_html_file_index_list_to_file()
    """
    file_tmp = open('valid_html_file_index_list.txt', 'r')
    valid_index_final = []
    for line in file_tmp.readlines():
        index_now = int(line.strip())
        valid_index_final.append(index_now)
    return valid_index_final

def mds_function(matrix):
    return

def hierarchy_clustering(matrix, featured_article_list):
    linkage_matrix = ward(matrix)
    fig, ax = plt.subplots(figsize=(15, 20))
    title_list = []
    for featured_article in featured_article_list:
        title_list.append(featured_article.title)
    ax = dendrogram(linkage_matrix, orientation="right", labels=title_list);
    plt.tick_params(
        axis= 'x',          # 使用 x 坐标轴
        which='both',      # 同时使用主刻度标签（major ticks）和次刻度标签（minor ticks）
        bottom='off',      # 取消底部边缘（bottom edge）标签
        top='off',         # 取消顶部边缘（top edge）标签
        labelbottom='off')
    plt.tight_layout()
    plt.savefig('ward_clusters.png', dpi=200)

def normalization(matrix):
    length = []

    for i in range(0,len(matrix)):
        for j in range(0, len(matrix)):
            if i == j:
                length.append(matrix[i][j])
    length_mean = 0
    for item in length:
        length_mean += item
    length_mean = length_mean/float(len(length))

    for i, item in enumerate(length):
        if length[i] == 0:
            length[i] = length_mean
    print length

    for i in range(0, len(matrix)):
        for j in range(0, len(matrix)):
            matrix[i][j] = matrix[i][j]/length[i]
    return matrix

def para_classification2file(featured_article_list):
    file_tmp = open('para_classification_1.txt', 'w')
    for featured_article in featured_article_list:
        file_tmp.write(featured_article.title+'\n')
        for sentence_list in featured_article.vector:
            file_tmp.write('Vector seperate\n')
            for sentence_obj in sentence_list:
                file_tmp.write(sentence_obj.original_form + '&&')
        file_tmp.write('Article seperate\n')


if __name__ == '__main__':
    # main(21)
    decision_tree_trained = train_f()
    matrix, featured_article_list = predict_f(decision_tree_trained)
    # 相似度矩阵归一化
    matrix_norm = normalization(matrix)
    gephi_edge_file = open('gephi_edge.csv','w')
    for i in range(0, len(matrix)):
        for j in range(0, len(matrix)):
            write_to_gephi_edge(i, j, matrix[i][j], gephi_edge_file)
    hierarchy_clustering(matrix_norm, featured_article_list)
    para_classification2file(featured_article_list)
