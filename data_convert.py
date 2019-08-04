import os


def data_convert():
        for file in os.listdir("./Pracownicy/"):

                work_file = open("./Pracownicy/" + file, "r", encoding="utf-8-sig")
                data = work_file.readlines()

                work_file = open("./Pracownicy/" + file, "w", encoding="utf-8-sig")

                for i,line in enumerate(data):
                        line = line.strip()
                        if "," in line:
                                if line.count(",") == 3:
                                        data[i] = line +  "," + "\n"


                work_file.writelines(data)