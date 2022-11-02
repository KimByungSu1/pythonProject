import os, datetime, csv, time, queue

from PyQt5.QtCore import *

# ##################################################################################
# 수신Data , ParseData 파일로 저장
# ##################################################################################

class myFile(QObject):
    def __init__(self):  # 객체 생성시 초기 세팅
        super(myFile, self).__init__()

        Today = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 2021-01-07 17:30:00 형식
        self.Year = Today[0:4] + '년'  # 2021년
        self.Month = Today[5:7] + '월'  # 1월
        self.Day = Today[8:10] + '일'  # 7일

        self.basedirectory = "./save"  # 실행파일 경로에 Save폴더
        self.yearDirectory = self.basedirectory + '/' + self.Year  # ./save/2021년
        self.monthDirectory = self.yearDirectory + '/' + self.Month  # ./save/2021년/1월
        self.dayDirectory = self.monthDirectory + '/' + self.Day  # ./save/2021년/1월/27일

        try:
            if not os.path.isdir(self.basedirectory):  # 프로그램 실행 경로에 save폴더 존재 확인 있으면 true, 없으면 false
                os.mkdir(self.basedirectory)  # save 폴더 생성

            if not os.path.isdir(self.yearDirectory):  # ./save/xxxx년 폴더가 없으면
                os.mkdir(self.yearDirectory)  # ./save/xxxx년 폴더 생성

            if not os.path.isdir(self.monthDirectory):  # ./save/xxxx년/X월 폴더가 없으면
                os.mkdir(self.monthDirectory)  # ./save/xxxx년/x월 폴더 생성

            if not os.path.isdir(self.dayDirectory):  # ./save/xxxx년/X월/xx일 폴더가 없으면
                os.mkdir(self.dayDirectory)  # ./save/xxxx년/x월/xx일 폴더 생성
        except:
            print('Folder 생성 error')

    def SaveToTXT(self, Data):  # Txt 파일 형식으로 저장.
        self.checkDate()  # 날짜 바뀌면 신규폴더 생성
        nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 2021-01-07 17:30:00 형식

        saveDirectory = self.dayDirectory
        #saveFilepath = saveDirectory + '/' + '(' + nowTime[11:13] + '0000' + ')' + '.txt'  # 파일 이름 (140000) 형식으로 txt생성.
        saveFilepath = saveDirectory + '/' + nowTime[:13] + '0000.txt'  # 파일 이름 2021-01-07 140000 형식으로 txt생성.
        splitData = Data.split('\n')

        for x in splitData:
            try:
                if not os.path.isfile(saveFilepath):  # xx일 폴더 내부에 txt파일이 없으면
                    with open(saveFilepath, 'w', encoding='latin-1') as f:  # 신규 txt파일 생성
                        f.write(x)
                else:  # 기존 파일이 있다면
                    with open(saveFilepath, 'a', encoding='latin-1') as f:  # 기존 txt파일에 내용추가
                        f.write(x)
            except:
                print('Folder 생성 또는 Append error')

    def SaveToHeaderTXT(self, Header, Data):  # header 붙이고 Txt 파일 형식으로 저장.
        self.checkDate()  # 날짜 바뀌면 신규폴더 생성
        nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 2021-01-07 17:30:00 형식

        saveDirectory = self.dayDirectory
        #saveFilepath = saveDirectory + '/' + '(' + nowTime[11:13] + '0000' + ')' + '.txt'  # 파일 이름 (140000) 형식으로 txt생성.
        saveFilepath = saveDirectory + '/' + Header + nowTime[:13] + '0000.txt'  # 파일 이름 Header 2021-01-07 14:00:00 형식으로 txt생성.
        splitData = Data.split('\n')

        for x in splitData:
            try:
                if not os.path.isfile(saveFilepath):  # xx일 폴더 내부에 txt파일이 없으면
                    with open(saveFilepath, 'w', encoding='latin-1') as f:  # 신규 txt파일 생성
                        f.write(x)
                else:  # 기존 파일이 있다면
                    with open(saveFilepath, 'a', encoding='latin-1') as f:  # 기존 txt파일에 내용추가
                        f.write(x)
            except:
                print('Folder 생성 또는 Append error')

    def SaveToCSV(self, Data):  # CSV 파일 형식으로 저장
        self.checkDate()  # 날짜 바뀌면 신규 폴더 생성
        nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 2021-01-07 17:30:00 형식

        saveDirectory = self.dayDirectory
       # saveFilepath = saveDirectory + '/' + '(' + nowTime[11:13] + '0000' + ')' + '.csv'  # 파일 이름 (140000) 형식으로 csv생성.
        saveFilepath = saveDirectory + '/' + nowTime[:13] + '0000.csv'  # 파일 이름 (2021-01-07 140000) 형식으로 csv생성.

        splitData = Data.split('\r\n')  #   문자끝 '\r\n'제거
        try:
            if not os.path.isfile(saveFilepath):  # csv파일이 없으면
                with open(saveFilepath, 'w', newline='') as csvfile:  # 신규 csv파일 생성
                    csvwr = csv.writer(csvfile)
                    try:
                        csvwr.writerow(splitData[0].split(','))
                    except:
                        print('CSV File Open error')
            else:  # 기존 파일이 있다면
                with open(saveFilepath, 'a', newline='') as csvfile:  # 기존 csv파일에 내용 추가
                    csvwr = csv.writer(csvfile)
                    try:
                        csvwr.writerow(splitData[0].split(','))
                    except:
                        print('CSV File Append error')
        except:
            print('CSV File or Folder 생성 error')

    def checkDate(self):  # 날짜가 바뀌면 새로운 폴더 생성
        Today = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 2021-01-07 17:30:00 형식
        Year = Today[0:4] + '년'  # 2021년
        Month = Today[5:7] + '월'  # 1월
        Day = Today[8:10] + '일'  # 7일

        if self.Year != Year:  # 연도가 같지 않으면
            self.Year = Year  # 연도 갱신

        if self.Month != Month:  # 달이 같지 않으면,
            self.Month = Month

        if self.Day != Day:  # 일이 같지 않으면,
            self.Day = Day

        self.yearDirectory = self.basedirectory + '/' + self.Year  # ./save/2021년__폴더명 갱신

        self.monthDirectory = self.yearDirectory + '/' + self.Month  # ./save/2021년/1월__폴더명 갱신

        self.dayDirectory = self.monthDirectory + '/' + self.Day  # ./save/2021년/1월/27일__폴더명 갱신

        try:
            if not os.path.isdir(self.basedirectory):  # 프로그램 실행 경로에 save폴더 존재 확인 있으면 true, 없으면 false
                os.mkdir(self.basedirectory)  # save 폴더 생성

            if not os.path.isdir(self.yearDirectory):  # ./save/xxxx년 폴더가 없으면
                os.mkdir(self.yearDirectory)  # ./save/xxxx년 폴더 생성

            if not os.path.isdir(self.monthDirectory):  # ./save/xxxx년/X월 폴더가 없으면
                os.mkdir(self.monthDirectory)  # ./save/xxxx년/x월 폴더 생성

            if not os.path.isdir(self.dayDirectory):  # ./save/xxxx년/X월/xx일 폴더가 없으면
                os.mkdir(self.dayDirectory)  # ./save/xxxx년/x월/xx일 폴더 생성
        except:
            print('Folder 생성 error')