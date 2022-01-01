# UOS-lecture-search
서울시립대학교의 강의와 강의계획서를 검색 및 조회하는 코드입니다.

cf. exe 파일로 만드는 법

1. pyinstaller 설치 후
2. cmd 실행 하고
3. 원하는 파이썬 파일이 있는 곳으로 디렉토리 변경
cd 디렉토리 경로
4. 아래 코드 실행
pyinstaller -F 시립대_api_수업계획서_2_exe.py
4-1. ico 파일이 있다면 아래 코드 실행
pyinstaller -F --icon=이루매.ico 시립대_api_수업계획서_2_exe.py
