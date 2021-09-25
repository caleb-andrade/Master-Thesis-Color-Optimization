from random import randint
from random import random
from copy import copy
import time

print 'UMBRAL DE ACEPTACIÓN CRONOGRAMA DE ENFRIAMIENTO EXPONENCIAL'
print '\n'

#Definimos las coordenadas de los 8 colores fundamentales en CIELUV

#Rojo
ro=[53.2405879437,175.021268996,37.7674609525]
#Amarillo
am=[97.1395070397,7.71662453296,106.807661295]
#Negro
ne=[0,0,0]
#Magenta
ma=[60.3235065274,84.0821945066,-108.664229814]
#Cyan
cy=[91.1133014407,-70.4667711742,-15.1763472196]
#Azul
az=[32.295672565,-9.40079676708,-130.330199078]
#Blanco
bl=[100.0,0.0122141319044,0.0288676011052]
#Verde
ve=[87.7350994883,-83.0667099615,107.417653548]

#Definimos la transformacion CIELUV ->XYZ
def T3(LUV):
    L=LUV[0]
    U=LUV[1]
    V=LUV[2]
    xn=0.3127
    yn=0.3290
    if LUV==[0,0,0]:
        X=Y=Z=0
    else:
        un=4*xn/(-2*xn+12*yn+3)
        vn=9*yn/(-2*xn+12*yn+3)
        
        if L<=0.008856*903.3:
            Y=L/903.3
        else:
            Y=((L+16)/116)**3
        if L==0:
            X=Y=Z=1000
        else:
            X=Y*9*(U+13*L*un)/(4*(V+13*L*vn))
            Z=(-15*Y-X+(52*L*X)/(U+13*L*un))/3
    return [X,Y,Z]

#Definimos la transformacion XYZ->RGBl
def T4(XYZ):
    R=3.240479*XYZ[0]-1.537150*XYZ[1]-0.498535*XYZ[2]
    G=-0.969256*XYZ[0]+1.875992*XYZ[1]+0.041556*XYZ[2]
    B=0.055648*XYZ[0]-0.204043*XYZ[1]+1.057311*XYZ[2]
    return [R,G,B]

#Definimos la transformacion inversa de la correccion gamma RGBl->sRGB
def G2(RGBl):
    sRGB=[]
    for i in range(3):
        if RGBl[i]<=0.0031308:
            sRGB.append(12.92*RGBl[i])
        else:
            sRGB.append(-0.055+1.055*RGBl[i]**(float(1)/2.4))
    return sRGB

#Definimos la correción gamma sRGB->RGBl
def G1(sRGB):
    RGBl=[0,0,0]
    for i in range(0,3):
        if sRGB[i]<=0.04045:
            RGBl[i]=sRGB[i]/12.92
        else:
            RGBl[i]=((sRGB[i]+0.055)/1.055)**2.4
    return RGBl
            
#Definimos la transformacion de RGBl->XYZ
def T1(RGBl):
    X=0.412453*RGBl[0]+0.357580*RGBl[1]+0.180423*RGBl[2]
    Y=0.212671*RGBl[0]+0.715160*RGBl[1]+0.072169*RGBl[2]
    Z=0.019334*RGBl[0]+0.119193*RGBl[1]+0.950227*RGBl[2]
    return [X,Y,Z]

#Definimos la transformacion de XYZ->CIELUV
def T2(XYZ):
    X=XYZ[0]
    Y=XYZ[1]
    Z=XYZ[2]
    xn=0.3127
    yn=0.3290
    if XYZ==[0,0,0]:
        L=U=V=0
    else:
        u=4*X/(X+15*Y+3*Z)
        v=9*Y/(X+15*Y+3*Z)
        un=4*xn/(-2*xn+12*yn+3)
        vn=9*yn/(-2*xn+12*yn+3)
        if Y<=0.008856:
            L=903.3*Y
        else:
            L=116*(Y**(float(1)/3))-16
        U=13*L*(u-un)
        V=13*L*(v-vn)
    return [L,U,V]

#Definimos una función que coloca n puntos iniciales aleatorios en CIELUV RGB
def ranpoints(m):
    V=[]
    for i in range(m):
        temp=[]
        for j in range(3):
            temp.append(random())
        V.append(T2(T1(G1(temp))))
    return V
        
#Definimos una función para añadir un elemento al final de la lista, si éste no está en ella
def Checklist(L,x):
    for i in range (len(L)):
        if x==L[i]:
            break
        if i==len(L)-1:
            L.append(x)

#Construimos una lista para almacenar los tetrahedros iniciales
T=[[],[],[],[],[],[]]

#Definimos una lista vacía para almacenar los vértices
V=[]

#Definimos un vector que almacene estos 8 colores básicos
C=[ro,am,ve,ne,ma,bl,cy,az]

#Construimos un vector que almacene las 4 particiones iniciales del RGBcube-CIELUV en 6 tetrahedros
CI=[[1,2,3,4,5,6,7,8],[2,3,4,1,6,7,8,5],[3,4,1,2,7,8,5,6],[4,1,2,3,8,5,6,7]]

#Construimos un vector que almacene los vértices de los 6 tetrahedros iniciales
TI=[[4,1,5,6],[4,8,5,6],[4,3,2,6],[4,3,7,6],[4,1,2,6],[4,8,7,6]]

#Definimos una función distancia entre dos vértices
def dist(X,Y):
    return ((X[0]-Y[0])**2+(X[1]-Y[1])**2+(X[2]-Y[2])**2)**0.5

n=input('Número de vértices deseados (n): ')
resp1=input('¿Desea solución inicial determinista(0) o aleatoria(1)?: ')

#Construimos la triangulación de Kuhn para la solución inicial determinista
if n>7 and resp1==0:
    conf=input('Configuración tetrahédrica inicial (1-4): ')
    t1=time.time()
    #Llenamos los tetrahedros
    for i in range (6):
        for j in range (4):
            ver=C[CI[conf-1][TI[i][j]-1]-1]
            T[i].append(ver)
            #Llenamos la lista de vértices, evitando duplicidad, para ello usamos Checklist
            if i==0:
                V.append(ver)
            else:
                Checklist(V,ver)

if n<8 and resp1==0:
    #Llenamos V con n<8, escogiendo al azar n de los 8 colores fundamentales.
    t1=time.time()
    while len(V)<n:
        ban=1
        vtemp=C[randint(1,8)-1]
        for j in range(len(V)):
            if dist(V[j],vtemp)==0:
                ban=0
                break
        if ban==1:
            V.append(vtemp)
            
#Definimos una función para construir las aristas de un tetrahedro, dados sus vértices
def Tet(T):
    A=[]
    for i in range(len(T)):
        for j in range (i+1,len(T)):
            A.append([T[i],T[j]])
    return A

#Definimos una función para verificar que dos aristas sean equivalentes
def Equi(A,B):
    x=0
    if (A[0]==B[0] and A[1]==B[1])or(A[0]==B[1] and A[1]==B[0]):
        x=1
    return x

#Definimos una función que busque la arista más larga en una lista de tetrahedros
def AristaMax(T):
    #Arista inicial:
    AM=[Tet(T[0])[0]]
    for i in range(len(T)):
        A=Tet(T[i])
        for j in range (6):
            #Vamos a guardar los índices de los tetrahedros donde esta arista aparezca
            if dist(A[j][0],A[j][1])> dist(AM[0][0],AM[0][1]):
                AM=[A[j]]
            if Equi(AM[0],A[j])==1:
                AM.append(i)
            
    return AM

#Definimos una función para determinar el punto medio entre dos vértices
def MidP(A,B):
    MP=[float(A[0]+B[0])/2,float(A[1]+B[1])/2,float(A[2]+B[2])/2]
    return MP

#Definimos una función que parte en dos tetrahedros a un tetrahedro por la mitad de su arista mayor
def SubTet(T):
    AM=AristaMax([T])
    #Calculamos el punto medio de la arista maxima   
    MP=MidP(AM[0][0],AM[0][1])
    i1=T.index(AM[0][0])
    i2=T.index(AM[0][1])
    #Definimos los subtetrahedros, insertando los dos primeros vértices a cada uno
    T1=[MP,T[i1]]
    T2=[MP,T[i2]]
    #Agregamos los vértices faltantes a ambos subtetrahedros
    for i in range (len(T)):
        if i!=i1 and i!=i2:
            T1.append(T[i])
            T2.append(T[i])
    return [T1,T2]

#Definimos una función que calcule el arista máxima (de una lista de tetras) y subdivida en dos a todos los tetrahedros que la contengan.
def LisTet(T):
    AM=AristaMax(T)
    for i in range (1,len(AM)):
        ST=SubTet(T[AM[i]])
        T[AM[i]]=ST[0]
        T.append(ST[1])
    return T

#Definimos una función para aplicar iterativamente LisTet hasta alcanzar los n vértices
def Solini(T,V,n):
    k=n-len(V)
    for j in range(k):
        AM=AristaMax(T)
        V.append(MidP(AM[0][0],AM[0][1]))
        T=LisTet(T,AM)
    return [T,V]

#Ahora aplicamos iterativamente la función anterior hasta alcanzar los n vértices deseados
if n>7 and resp1==0:
    for i in range (n-len(V)):
        AM=AristaMax(T)
        V.append(MidP(AM[0][0],AM[0][1]))
        T=LisTet(T)

if resp1==1:
    t1=time.time()
    V=ranpoints(n)

t2=time.time()
tiempsolini=t2-t1

#Definimos una función para añadir una arista al final de la lista, si ésta no está en ella
def AChecklist(L,x):
    if len(L)==0:
        L.append(x)        
    for i in range (len(L)):
        if Equi(L[i],x)==1:
            break
        if i==len(L)-1:
            L.append(x)
    return L
    
#Hacemos una función que extraiga una lista de las aristas sin repetición
def Arista(T):
    A=[]
    for i in range (len(T)):
        Ar=Tet(T[i])
        for j in range (6):
            #Llenamos la lista de aristas, evitando duplicidad, para ello usamos AChecklist
            if i==0:
                A.append(Ar[j])
            else:
                AChecklist(A,Ar[j])
    return A

#Construimos las aristas de la malla para graficarla
if n>7 and resp1==0:
    A=Arista(T)
    
if n<8 and resp1==0:
    A=[]
    for i in range(n-1):
        for j in range(i+1,n):
            A.append([V[i],V[j]])

if resp1==1:
    A=[]
    for i in range(len(V)-1):
        for j in range(i+1,len(V)):
            A.append([V[i],V[j]])

#Escribimos las coordenadas en un archivo para ser leído y graficado
filename='tetra.txt'
arch=open (filename,'w')
for i in range (len(A)):
    arch.write(str(A[i][0][0])+'\t'+str(A[i][0][1])+'\t'+str(A[i][0][2])+'\n\n')
    arch.write(str(A[i][1][0])+'\t'+str(A[i][1][1])+'\t'+str(A[i][1][2])+'\n\n\n')
arch.close()

#Definimos una función para calcular la distancia min de un vértice al resto de los vértices en una lista
def DistV(V,i):
    D0=dist(V[0],V[1])
    for j in range(len(V)):
        if i!=j:
            D=dist(V[i],V[j])
            if D<D0:
                D0=D
    return D0

#Definimos una función para calcular la distancia mínima entre los vértices de una lista V.
def Dmin(V):
    D0=dist(V[0],V[1])
    for i in range(len(V)):
        D=DistV(V,i)
        if D<D0:
            D0=D
    return D0

#Definimos una funcion que calcula la distancia mínima entre los vértices de una lista y devuelve los índices de los vértices en cuestión.
def Dv1v2(V):
    D0=dist(V[0],V[1])
    ind1=0
    ind2=1
    for i in range (len(V)-1):
        for j in range (i+1,len(V)):
            D=dist(V[i],V[j])
            if D<D0:
                D0=D
                ind1=i
                ind2=j
    return [D0,ind1,ind2]



#ETAPA DE OPTIMIZACIÓN

#Definimos una función que proyecta ortogonalmente las imágenes inversas de vértices que no estén dentro del RGB cube.
def ProInv(v):
    x=G2(T4(T3(v)))
    if x[0]<0:
        x[0]=0
    if x[0]>1:
        x[0]=1
    if x[1]<0:
        x[1]=0
    if x[1]>1:
        x[1]=1
    if x[2]<0:
        x[2]=0
    if x[2]>1:
        x[2]=1
    return T2(T1(G1(x)))

#Definimos una función que evalúa si la imagen inversa de v está en el RGB cube.
def ImInv(v):
    temp=0
    x=G2(T4(T3(v)))
    if 0<=x[0]<=1 and 0<=x[1]<=1 and 0<=x[2]<=1:
        temp=1
    return temp

#Ajustamos la lista inicial de vertices V, revisando que las imágenes inversas estén dentro del RGB cube, si no, proyectamos ortogonalmente sobre el RGB cube
for i in range(len(V)):
    if ImInv(V[i])==0:
        V[i]=ProInv(V[i])

#Definimos una función para escoger aleatoriamente un punto en una vecindad de v0.
def Vecino(v,delta):
    w=[]
    for i in range(3):
        ran=-1+2*random()
        w.append(v[i]+delta*ran)
    return w

#Definimos una función que encuentra aleatoreamente un vecino en la delta-vecindad de v cuya imagen inversa esta en el RGB cube
def VAcep(v,delta):
    x=Vecino(v,delta)
    while ImInv(x)==0:
        x=Vecino(v,delta)
    return x

#PARAMETROS DEL ALGORITMO
deltaini=[25,15,20,25,20,17.5,10,10,10]
tempini=[20.129,13.088,15.265,15.724,13.7771606445,11.567,8.511,8.176,8.21789529324]

if n>10 and n<=50:
    index=1+(n-11)/5
    delta=deltaini[index]
    T0=tempini[index]
if n<=10:
    index=0
    delta=deltaini[index]
    T0=tempini[index]
L=input('Valor de Lambda: ')
Fi=float(raw_input('Factor de enfriamiento: '))
Ld=20
criterio=input('¿Cual criterio de paro desea usar? Cero virtual=0, Numero de iteraciones=1: ')

if criterio==0:
    epsilon=float(raw_input('Cero virtual: '))
    Iter=1000000
if criterio==1:
    Iter=input('Iteraciones: ')
    epsilon=0


#Vectores para guardar las funciones objetivos cada vez que se acepto un movimiento, temporal por ciclo de recocido y total
LV=[]
LVfinal=[]
#Vector para guardar los promedios de las lambda-funciones objetivo aceptadas para una temperatura dada
Prom=[0]
#Realizamos una copia de V
V0=copy(V)
V1=copy(V)
#Inicializamos contadores para las iteraciones,aceptaciones y tiempo
it=0
it2=0
it3=0
it4=0
acep=0
t1=time.time()

#Definimos una función que proponga un movimiento (que puede ser aceptado o rechazado) para los elementos de la lista V
def Recocido(V,V0,D0,D0max,delta,T0):

    cont=0
                   
    #Se escoge el índice del vértice a mover al azar.
    ind=Dv1v2(V)[randint(1,2)]
    
    #Se propone un vecino aleatorio factible
    v0=VAcep(V[ind],delta)
    vtemp=V[ind]
    V[ind]=v0
    D0temp=DistV(V,ind)

    if D0temp>D0-T0:
        #Acepto movimiento, paso el criterio de aceptacion
        cont=1

        if D0temp>D0:
            #Se verifica el valor de D0
            D0=Dmin(V)
            if D0>D0max:
                #Si el valor de D0max se mejora.
                V0=copy(V)
                D0max=D0

        if D0temp<=D0:
            D0=D0temp
                                                       
    else:
        #No se aceptó movimiento, se vuelve al valor original de V
        V[ind]=vtemp
   
    return [V,V0,D0,D0max,cont]

#Vamos a escribir en un archivo los cambios de temperatura para graficarlos
filename4='temperatura.txt'
arch4=open(filename4,'w')

D0max=Dmin(V0)
D0=Dmin(V)
D0ini=D0
D0opt=0

if n>50:
    delta=T0=D0

print 'Delta inicial: ',delta
print 'Temperatura inicial: ',T0

#Etapa de optimizacion 
while T0>epsilon and it<Iter:
       
    Res=Recocido(V1,V0,D0,D0max,delta,T0)
    V1=Res[0]
    V0=Res[1]
    D0=Res[2]
    D0max=Res[3]
    cont=Res[4]
    
    acep=acep+cont
    if cont>0:
        LV.append(D0)
        LVfinal.append(D0)
        it3=0

    if D0max>D0opt:
        D0opt=D0max
        it2=acep
        t3=time.time()
        
    if len(LV)==L:
        suma=0
        for i in range(L):
            suma=suma+LV[i]
        pr=suma/L
        Prom.append(pr)
        LV=[]
        if Prom[len(Prom)-1]<=Prom[len(Prom)-2]:
            T0=Fi*T0
            arch4.write(str(acep)+'\t'+str(LVfinal[acep-1])+'\n')
                
    it=it+1
    it3=it3+1

    if it3==2*Ld:
        delta=float(delta)/2
        it3=0
        print 'Se reduce delta: ',delta
t2=time.time()
arch4.close()

#Definimos una función que ajusta las imagenes inversas a la rejilla de 256x256x256 del RGB cube
def ImInv2(v):
    x=G2(T4(T3(v)))
    y=[round(255*x[0]),round(255*x[1]),round(255*x[2])]
    x=[y[0]/255,y[1]/255,y[2]/255]
    return T2(T1(G1(x)))

#Ajustamos la lista de vertices V0 utilizando ImInv2
for i in range(len(V0)):
    V0[i]=ImInv2(V0[i])

D0max=Dmin(V0)

print '\n'
print 'Función objetivo inicial: ',D0ini
print 'Función objetivo óptima: ',D0max
print 'Temperatura final: ',T0
print 'Iteraciones totales: ',it
print 'Aceptaciones totales: ',acep
print 'Porcentaje de aceptacion: ',int(round(float(acep)*100/it)),'%'
print 'T cálculo sol. inicial (seg): ',tiempsolini
print 'T cálculo etapa de optimización (seg): ',t2-t1
print 'T total de calculo (seg): ',tiempsolini+t2-t1,'seg'
print 'Aceptación donde apareció el óptimo: ',it2
print 'T donde apareció el óptimo (seg): ',t3-t1 
print '\n'

#Escribimos el valor de la iteración donde apareció el óptimo 
filename6='optimo.txt'
arch6=open(filename6,'w')
arch6.write(str(it2)+'\t'+str(LVfinal[it2-1])+'\n')
arch6.close()

#Se escriben la coordenadas de los vértices optimizados, y de su color correspondiente (ULTIMA CORRIDA)
filename2='recocido.txt'
arch2=open(filename2,'w')
x=[]
for i in range(len(V0)):
    col=(G2(T4(T3(V0[i]))))
    x.append([round(255*col[0]),round(255*col[1]),round(255*col[2])])
    arch2.write(str(V0[i][0])+'\t'+str(V0[i][1])+'\t'+str(V0[i][2])+'\t'+str(x[i][0])+'\t'+str(x[i][1])+'\t'+str(x[i][2])+'\n')
arch2.close()

#Se escribe el historial de aceptación para ser graficado 
filename3='historial.txt'
arch3=open(filename3,'w')
for i in range(len(LVfinal)):
    arch3.write(str(LVfinal[i])+'\n')
arch3.write(str('#valor de n: ')+str(n))
arch3.close()

#Definimos una función que ordene los colores, dependiendo de su cercanía a los ocho vértices del cubo RGB
def Orden(V):
    temp=[[],[],[],[],[],[],[],[]]
    C=[ro,am,ve,cy,az,ma]
    for j in range(len(V)):
        Dimi=400
        for i in range(len(C)):
            D=dist(C[i],V[j])
            if D<=Dimi:
                index=i
                Dimi=D

        D=dist(V[j],ne)     
        if len(temp[index])>0:
            for i in range(len(temp[index])):
                if D<temp[index][i][0]:
                    temp[index].insert(i,[D,V[j]])
                    break
                if i==len(temp[index])-1:
                    temp[index].append([D,V[j]])

        if len(temp[index])==0:
            temp[index].append([D,V[j]])
            
    temp2=[]
    for j in range(len(temp)):
        for i in range(len(temp[j])):
            temp2.append([j+1,i+1,temp[j][i][1]])
    
    return temp2
    
#Escribimos en un archivo la lista de colores "ordenada" 
filename9='colores.txt'
arch9=open(filename9,'w')
Col=Orden(V0)
for i in range(len(Col)):
    col=(G2(T4(T3(Col[i][2]))))
    z=[round(255*col[0]),round(255*col[1]),round(255*col[2])]
    arch9.write(str(Col[i][0])+'\t'+str(Col[i][1])+'\t'+str(z[0])+'\t'+str(z[1])+'\t'+str(z[2])+'\n')
arch9.close()

#Definimos una función que calcule cuantos vértices se encuentran a una cercanía epsilon de cada vértice, y sus índices. 
def Depsilon(V,e,D0):
    Epsi=[]
    for i in range(len(V)):
        temp=[0]
        for j in range(len(V)):
            if i!=j:
                if dist(V[i],V[j])<D0+e:
                    temp[0]=temp[0]+1
                    temp.append(j)
        Epsi.append(temp)
    return Epsi


#Hacemos una lista de las aristas de los epsilon-vecinos
B=[]
e=0.05*D0
Epsi=Depsilon(V0,e,D0)
for i in range(len(Epsi)):
    if len(Epsi[i])>1:
        for j in range(len(Epsi[i])-1):
            if i==0:
                B.append([V0[i],V0[Epsi[i][j+1]]])
            else:
                AChecklist(B,[V0[i],V0[Epsi[i][j+1]]])
                                
#Escribimos las coordenadas en un archivo para ser leído y graficado
filename5='epsilon.txt'
arch5=open(filename5,'w')
for i in range (len(B)):
    arch5.write(str(B[i][0][0])+'\t'+str(B[i][0][1])+'\t'+str(B[i][0][2])+'\n\n')
    arch5.write(str(B[i][1][0])+'\t'+str(B[i][1][1])+'\t'+str(B[i][1][2])+'\n\n\n')
arch5.close()

    






   
