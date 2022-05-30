def create_generator():
    print("Iniciou a função")
    mylist = range(3)
    for i in mylist:
        yield i * i
    print("Finalizou da função")


print("PARTE 1")

mygenerator = create_generator()

print(type(mygenerator))

print("PARTE 2")

for i in mygenerator:
    print(i)
