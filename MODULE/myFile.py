import os

def imgFolderList():         #   이미지 폴더 및 파일 딕셔너리 형태로 반환
    dir_path = './IMAGE'
    resDict = {}

    for item in os.listdir(dir_path):       #   dir_path 경로에 존재하는 폴더
        resDict[item] = []                              #   '폴더명':[] 형태로 만들기

    for folder in resDict.keys():                     #   '폴더명':[] list 안에 파일 넣기
        newFolderPath = dir_path + '/' + folder
        fileList = []
        for item in os.listdir(newFolderPath):
            fileList.append(os.path.join(os.path.abspath(newFolderPath), item))

        resDict[folder] = fileList

    return resDict