#r	Opens a file for reading (default)
#w	Open a file for writing. If a file already exists, it deletes all the existing contents and adds new content from the start of the file.
#x	Open a file for exclusive creation. If the file already exists, this operation fails.
#a	Open a file in the append mode and add new content at the end of the file.
#b	Open the file in binary mode.
#t	Opens a file in a text mode (default).
#+	Open a file for updating (reading and writing).
try:
    fp = open (r'C:\Users\paulo\PycharmProjects\pythonProject\FILES/data.json', 'r')
    print(fp.read())
    fp.close()
except FileNotFoundError:
    print("Please check the path.")
finally:
    print("Exit")