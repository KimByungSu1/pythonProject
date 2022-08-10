import os

def imgFolderList():         #   이미지 폴더 및 파일 딕셔너리 형태로 반환
    dir_path = './IMAGE'
    resList = []
    resDict = {}

    for item in os.listdir(dir_path):
        if os.path.isdir(os.path.join(dir_path, item)):     #   폴더라면
            resDict[item] = resList                         #   '폴더명':[] 형태로 변경

    for folder in list(resDict.keys()):
        newFolderPath = dir_path + '/' + folder
        fileList = []
        for item in os.listdir(newFolderPath):
            if os.path.isfile(os.path.join(newFolderPath, item)):  # 폴더라면
                fileList.append(item)
        resDict[folder] = fileList

    return resDict