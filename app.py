from flask import Flask, request, jsonify
import re
import requests
import xml.etree.ElementTree as ET

application = Flask(__name__)

@application.route("/subject_search", methods=['POST'])
def subject():
    req = request.get_json()

    params = req['action']['params']  # 사용자의 발화로부터 추출한 파라미터 정보 / 엔티티의 이름을 키로, 추출한 정보를 상세 값으로
    subjectNm, year, term = params['subject_name'], params['year'], params['term']
    year = re.sub(r'[^0-9]', '', year)  # 숫자만 추출: https://codechacha.com/ko/python-extract-integers-from-string/
    term = re.sub(r'[^1-2]', '', term)
    apiKey = 1234 # github에는 업로드 X

    url = f"https://wise.uos.ac.kr/uosdoc/api.ApiApiSubjectList.oapi?apiKey={apiKey}2&year={year}&term=A{term}0&subjectNm={subjectNm}"
    response = requests.get(url).text

    common = dict()
    each_subj = [dict()]  # [{}, {week:~, class_cont:~, ...}, {week:~, class_cont:~, ...}, ~~~]
    each_subj_tag_set = {'subject_no', 'subject_nm', 'class_div', 'subject_div', 'dept', 'prof_nm'}
    translate = {'subject_no': '교과번호', 'subject_nm': '교과목명', 'class_div': '분반', 'subject_div': '전공필수/선택',
                 'dept': '학부(과)',
                 'prof_nm': '담당교수 성명', 'tel_no': '담당교수 연락처', 'score_eval_rate': '성적평가 정보', 'book_nm': '교재',
                 'lec_goal_descr': '교과목 설명', 'curi_edu_goal_nm': '수업 목표', 'week': '주', 'class_cont': '수업내용',
                 'class_meth': '수업방법', 'week_book': '수업 교재', 'prjt_etc': '준비물, 과제, 기타 정보'}

    message = ''

    try:
        root = ET.fromstring(response)
        subject_tree = root[0]
        length = len(subject_tree)
        if length:
            for num in range(length):
                info = subject_tree[num]
                subj_dict = dict()
                for information in info:
                    if information.tag in each_subj_tag_set:
                        subj_dict[information.tag] = information.text
                each_subj.append(subj_dict)

            for i in range(1, length + 1):
                message += f"{i}번째 검색결과입니다.\n"
                subj_inform = each_subj[i]
                for element in subj_inform:
                    if subj_inform[element] is not None:
                        no_enter_list = subj_inform[element].split('\n')
                        no_enter = ' '.join(no_enter_list)
                        no_tab_list = no_enter.split('\t')
                        no_tab = '  '.join(no_tab_list)
                        if element in translate:
                            message += f'{translate[element]}은(는) {no_tab.strip()} 입니다.\n'
                if i != len(subject_tree):
                    message += '\n'
        else:
            message = "검색 결과가 존재하지 않습니다."
    except:
        message = '입력이 올바른지 확인해주세요!'
    # print(message)
    res = {
        "contents": [
            {
                "type": "text",
                "text": f"{message}"
            }
        ]
    }

    # 전송
    return jsonify(res)


@application.route("/syllabus_search", methods=['POST'])
def syllabus():
    req = request.get_json()

    params = req['action']['params']  # 사용자의 발화로부터 추출한 파라미터 정보 / 엔티티의 이름을 키로, 추출한 정보를 상세 값으로
    subjectNo, classDiv, year, term = params['subject_no'], params['class_div'], params['year'], params['term']
    classDiv = re.sub(r'[^0-9]', '', classDiv)
    if len(classDiv) == 1:
        classDiv = '0' + classDiv
    year = re.sub(r'[^0-9]', '', year)
    term = re.sub(r'[^1-2]', '', term)
    apiKey = 1234 # github에는 업로드 X

    url = f"https://wise.uos.ac.kr/uosdoc/api.ApiApiCoursePlanView.oapi?apiKey={apiKey}&year={year}&term=A{term}0&subjectNo={subjectNo}&classDiv={classDiv}"
    response = requests.get(url).text

    common = dict()
    each_week = [dict()]  # [{}, {week:~, class_cont:~, ...}, {week:~, class_cont:~, ...}, ~~~]
    each_week_tag_set = {'week', 'class_cont', 'class_meth', 'week_book', 'prjt_etc'}
    translate = {'subject_no': '교과번호', 'subject_nm': '교과목명', 'prof_nm': '담당교수 성명', 'tel_no': '담당교수 연락처',
                 'score_eval_rate': '성적평가 정보', 'book_nm': '교재', 'lec_goal_descr': '교과목 설명', 'curi_edu_goal_nm': '수업 목표',
                 'week': '주', 'class_cont': '수업내용', 'class_meth': '수업방법', 'week_book': '수업 교재',
                 'prjt_etc': '준비물, 과제, 기타 정보'}
    message = ''

    try:
        root = ET.fromstring(response)
        subject_tree = root[0]
        for week_num in range(16):
            week_info = subject_tree[week_num]
            week = week_num + 1
            week_dict = dict()
            for information in week_info:
                if information.tag not in each_week_tag_set and information.tag not in common:
                    common[information.tag] = information.text
                elif information.tag in each_week_tag_set:
                    week_dict[information.tag] = information.text
            each_week.append(week_dict)

        for element in common:
            if not common[element] is None:
                no_enter_list = common[element].split('\n')
                no_enter = ' '.join(no_enter_list)
                no_tab_list = no_enter.split('\t')
                no_tab = '  '.join(no_tab_list)
                if element in translate:
                    message += f"{translate[element]}은(는) {no_tab.strip()} 입니다.\n\n"

        for i in range(1, 17):
            message += f"{i}주차의\n"
            week_inform = each_week[i]
            for element in week_inform:
                if element != 'week' and week_inform[element] is not None:
                    no_enter_list = week_inform[element].split('\n')
                    no_enter = ' '.join(no_enter_list)
                    no_tab_list = no_enter.split('\t')
                    no_tab = '  '.join(no_tab_list)
                    if element in translate:
                        message += f'{translate[element]}은(는) {no_tab.strip()} 입니다.\n'
            if i != 16:
                message += '\n'
    except:
        message = '입력이 올바른지 확인해주십시오.'

    res = {
        "contents": [
            {
                "type": "text",
                "text": f"{message}"
            }
        ]
    }

    # 전송
    return jsonify(res)


if __name__ == "__main__":
    application.run(host='0.0.0.0', port=5000)
