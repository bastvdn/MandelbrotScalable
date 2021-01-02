X = [1,2,3,4,5]
Y = [10,20,30,40,50]

Z = [complex(x,y) for y in Y for x in X]

print(Z)