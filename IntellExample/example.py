array=[]
#Считывание файла
def readfile():
    f= open('book.txt', 'r') 
    str1 = [str.strip() for str in f]
    f.close() 
    for item in str1:
        global array
        items=item.split(' ')
        array.append((str(items[0]),str(items[1]),int(items[2])))
    return array
    
readfile()
M = []

#Добавление данных в общий массив
def addArr():
    for i in range(len(array)):
        for j in range(len(array[i])):
            M.append(array[i][j])
    return(M)
addArr()

A1 = []#Книга
N = []
A2 = []#Жанр
A3 = []#Оценка

#Выводим данные для Книги в массив
def book():
    for k in range(len(M)):
        if(k%3==0):
            A1.append(M[k])
        else:
            N.append(M[k])
book()

#Выводим данные для Жанра и Оценки
def markGen():
    for l in range(len(N)):
        if (l%2==0):
            A2.append(N[l])
        else:
            A3.append(N[l])
            
markGen()
Books=[]
for l in range(len(A3)):
    Books.append([A1[l],A2[l],A3[l]])

#Выводим подходящие к выбранной книге произведения по жанру и оценке
def res(numBooks,Books,asseg,J):
    index=0
    BooksJ=[elem for elem in Books if (elem[1]==J)]
    BooksJ=sorted(BooksJ,key=lambda book:book[2])
    for l in range(len(BooksJ)):
        if (BooksJ[l][2]==asseg):
            index=l
            break
    dispers=int(numBooks/2) #Дисперсия
    if (index-dispers<0):
        index=dispers
    elif (index>=(len(BooksJ)-dispers)):
        index=len(BooksJ)-dispers-1
    return BooksJ[index-dispers:index+dispers+1]

print(res(3,Books,7,"Поэма"))

    
    

        
        
        
    
    








